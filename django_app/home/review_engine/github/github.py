## github pull request api docs: https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#list-pull-requests-files

import os
import re
import uuid
from pathlib import Path
from urllib.parse import urlparse
import requests
from django_app.home.review_engine.llm.ai_agent import analyze_code_llm
from dotenv import load_dotenv

# load env file 
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env", override=False)


class PRReviewError(Exception):
    def __init__(self, message, code="pr_review_error", status_code=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


#==================== Helper Functions ===================
def get_owner_repo(url):
    if not url or not str(url).strip():
        raise PRReviewError("Repository URL is required.", code="missing_repo_url", status_code=400)

    parsed_url = urlparse(str(url).strip())
    host = parsed_url.netloc.lower().replace("www.", "")

    if host != "github.com":
        raise PRReviewError(
            "Only GitHub repository URLs are supported right now. Use a format like https://github.com/owner/repo.",
            code="invalid_repo_url",
            status_code=400,
        )

    path_parts = [part for part in parsed_url.path.split("/") if part]
    if len(path_parts) < 2:
        raise PRReviewError(
            "Repository URL must include both the owner and repo name, for example: https://github.com/owner/repo",
            code="invalid_repo_url",
            status_code=400,
        )

    owner = path_parts[0]
    repo = path_parts[1].removesuffix(".git")

    if not owner or not repo:
        raise PRReviewError(
            "The repository URL is incomplete or invalid.", 
            code="invalid_repo_url", 
            status_code=400
    )

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
def extract_changed_lines(patch):
    changed_lines = []
    old_line_number = None
    new_line_number = None

    for line in patch.splitlines():
        if line.startswith("@@"):
            hunk = re.match(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if hunk:
                old_line_number = int(hunk.group(1))
                new_line_number = int(hunk.group(2))
            continue

        if old_line_number is None or new_line_number is None or line.startswith("\\"):
            continue

        if line.startswith("+"):
            changed_lines.append(f"+ [new line {new_line_number}] {line[1:]}")
            new_line_number += 1
        elif line.startswith("-"):
            changed_lines.append(f"- [old line {old_line_number}] {line[1:]}")
            old_line_number += 1
        elif line.startswith(" "):
            old_line_number += 1
            new_line_number += 1

    return "\n".join(changed_lines)


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
            status_code=exc.response.status_code if hasattr(exc, "response") and exc.response is not None else None,
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
            status_code=exc.response.status_code if hasattr(exc, "response") and exc.response is not None else None,
        ) from exc


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
                code="invalid_pr_number",
                status_code=400
            )

        if pr_number <= 0:
            raise PRReviewError(
                "PR number must be greater than zero.", 
                code="invalid_pr_number",
                status_code=400
            )

        pr_files = fetch_pr_files(repo_url, pr_number, github_token)
        all_analyze_results = []

        for file in pr_files:
            if file.get("status") == "removed":
                continue

            file_name = file.get("filename")
            if not file_name:
                continue

            patch = file.get("patch")
            if not isinstance(patch, str):
                all_analyze_results.append(
                    {
                        "file_name": file_name,
                        "result": None,
                        "error": "GitHub did not provide a text diff for this file, so it was skipped.",
                        "error_code": "diff_unavailable",
                        "status_code": None,
                    }
                )
                continue

            changed_lines = extract_changed_lines(patch)
            if not changed_lines:
                all_analyze_results.append(
                    {
                        "file_name": file_name,
                        "result": None,
                        "error": "No added or deleted lines were available for this file, so it was skipped.",
                        "error_code": "no_changed_lines",
                        "status_code": None,
                    }
                )
                continue

            analyze_result = analyze_code_llm(changed_lines, file_name)
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
