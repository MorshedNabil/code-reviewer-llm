## github pull request api docs: https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#list-pull-requests-files

import base64
import os
import uuid
from urllib.parse import urlparse

import requests
from home.utils.ai_agent import analyze_code_llm
from home.utils.env import load_env_files


load_env_files(__file__)


class PRReviewError(Exception):
    def __init__(self, message, code="pr_review_error", status_code=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


#==================== Helper Functions ===================
def get_owner_repo(url):
    if not url or not str(url).strip():
        raise PRReviewError("Repository URL is required.", code="missing_repo_url")

    parsed_url = urlparse(str(url).strip())
    host = parsed_url.netloc.lower().replace("www.", "")

    if host != "github.com":
        raise PRReviewError(
            "Only GitHub repository URLs are supported right now. Use a format like https://github.com/owner/repo.",
            code="invalid_repo_url",
        )

    path_parts = [part for part in parsed_url.path.split("/") if part]
    if len(path_parts) < 2:
        raise PRReviewError(
            "Repository URL must include both the owner and repo name, for example: https://github.com/owner/repo",
            code="invalid_repo_url",
        )

    owner = path_parts[0]
    repo = path_parts[1].removesuffix(".git")

    if not owner or not repo:
        raise PRReviewError("The repository URL is incomplete or invalid.", code="invalid_repo_url")

    return repo, owner
# ========================================================


def _github_headers(github_token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    return headers


def _handle_github_error(response, action_label):
    status_code = response.status_code if hasattr(response, "status_code") else None
    message = response.text.strip() if hasattr(response, "text") else ""

    if status_code == 404:
        raise PRReviewError(
            f"{action_label} was not found. Please check the repository URL and PR number.",
            code="not_found",
            status_code=status_code,
        )
    if status_code == 401:
        raise PRReviewError(
            "GitHub authentication failed. Please check your token or use a public repository.",
            code="unauthorized",
            status_code=status_code,
        )
    if status_code == 403:
        raise PRReviewError(
            "GitHub access is temporarily limited or rate-limited. Please try again later or provide a valid token.",
            code="forbidden",
            status_code=status_code,
        )
    if message:
        raise PRReviewError(
            f"GitHub request failed while {action_label.lower()}: {message}",
            code="github_api_error",
            status_code=status_code,
        )
    raise PRReviewError(
        f"GitHub request failed while {action_label.lower()}.",
        code="github_api_error",
        status_code=status_code,
    )


#==================== GitHub API Functions ===================
def fetch_pr_files(repo_url, pr_number, github_token=None):
    repo, owner = get_owner_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = _github_headers(github_token)

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            _handle_github_error(response, "Fetching PR files")
        return response.json()
    
    except requests.RequestException as exc: # it's a network error, timeout, or other request-related issue. So no need to check the status code here, just raise a PRReviewError with a connection error message.
        raise PRReviewError(
            f"Unable to connect to GitHub while fetching PR files: {exc}",
            code="github_connection_error",
        ) from exc


def fetch_pr_details(repo_url, pr_number, github_token=None):
    """
    Fetches the details of a pull request from GitHub.
    """

    repo, owner = get_owner_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = _github_headers(github_token)

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            _handle_github_error(response, "Fetching PR details")
        return response.json()
    
    except requests.RequestException as exc:
        raise PRReviewError(
            f"Unable to connect to GitHub while fetching PR details: {exc}",
            code="github_connection_error",
        ) from exc


def fetch_file_content(repo_url, file_path, ref, github_token=None):
    """
    Fetches the content of a file from a GitHub repository at a specific reference (commit SHA, branch, or tag).
    """

    repo, owner = get_owner_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={ref}"
    headers = _github_headers(github_token)

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            _handle_github_error(response, "Fetching file content")

    except requests.RequestException as exc:
        raise PRReviewError(
            f"Unable to fetch file content for '{file_path}' from GitHub: {exc}",
            code="github_connection_error",
        ) from exc

    response_dict = response.json()
    try:
        file_content = base64.b64decode(response_dict.get("content", "")).decode("utf-8")
        return file_content
    except (KeyError, ValueError, UnicodeDecodeError):
        return None


# ================= The main function from where the pr request files will be analyzed ==================
def analyze_pr(repo_url, pr_number, github_token=None):
    github_token = github_token or os.environ.get("GITHUB_API_KEY")
    task_id = str(uuid.uuid4())

    try:
        if pr_number is None:
            raise PRReviewError("PR number is required.", code="missing_pr_number")

        try:
            pr_number = int(pr_number)

        except (TypeError, ValueError):
            raise PRReviewError(
                "PR number must be a valid integer.", 
                code="invalid_pr_number"
            )

        if pr_number <= 0:
            raise PRReviewError(
                "PR number must be greater than zero.", 
                code="invalid_pr_number"
            )

        pr_details = fetch_pr_details(repo_url, pr_number, github_token)
        head_sha = pr_details["head"]["sha"]

        if not head_sha:
            raise PRReviewError(
                "The PR metadata is incomplete and the head commit could not be resolved.",
                code="invalid_pr_data",
            )

        pr_files = fetch_pr_files(repo_url, pr_number, github_token)
        all_analyze_results = []

        for file in pr_files:
            if file.get("status") == "removed":
                continue

            file_name = file.get("filename")
            if not file_name:
                continue

            try:
                raw_content = fetch_file_content(repo_url, file_name, head_sha, github_token)
            except PRReviewError as exc:
                all_analyze_results.append(
                    {
                        "file_name": file_name,
                        "result": None,
                        "error": exc.message,
                        "error_code": exc.code,
                    }
                )
                continue

            if raw_content is None:
                all_analyze_results.append(
                    {
                        "file_name": file_name,
                        "result": None,
                        "error": "This file could not be read from GitHub and was skipped.",
                        "error_code": "file_unreadable",
                    }
                )
                continue

            analyze_result = analyze_code_llm(raw_content, file_name)
            all_analyze_results.append({"file_name": file_name, "result": analyze_result})

        if not all_analyze_results:
            return {
                "task_id": task_id,
                "status": "completed",
                "message": "No reviewable file changes were found for this pull request.",
                "all_analyze_results": [],
            }

        return {
            "task_id": task_id,
            "status": "completed",
            "all_analyze_results": all_analyze_results,
        }

    except PRReviewError as exc:
        return {
            "task_id": task_id,
            "status": "error",
            "error": {
                "code": exc.code,
                "message": exc.message,
                "status_code": exc.status_code,
            },
        }

    except Exception as exc:
        return {
            "task_id": task_id,
            "status": "error",
            "error": {
                "code": "unexpected_error",
                "message": f"An unexpected error occurred while reviewing the pull request: {exc}",
                "status_code": None,
            },
        }
