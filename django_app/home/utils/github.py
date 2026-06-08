## github pull request api docs: https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#list-pull-requests-files

import base64
from urllib.parse import urlparse
import os
import requests
import uuid
from home.utils.ai_agent import analyze_code_llm
from home.utils.env import load_env_files


load_env_files(__file__)

#==================== Helper Functions ===================
def get_ower_repo(url):
    parsed_url = urlparse(url)
    url_parts = parsed_url.path.strip("/").split("/")

    if len(url_parts) >= 2:
        owner, repo = url_parts[0], url_parts[1]
        return repo, owner
    return None, None


def fetch_pr_files(repo_url, pr_number, github_token=None):
    repo, owner = get_ower_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files" # api link for fetching pull request files
    header = {"Authorization": f"Bearer {github_token}"} if github_token else {}
    
    response = requests.get(url, headers=header) # as the api is a get method so using get() function

    response.raise_for_status() # This automatically throws an error if request failed. like this: 404 → PR not found; 403 → rate limit exceeded; 401 → invalid token
    return response.json() # convert the response from json format to python dictionary


def fetch_pr_details(repo_url, pr_number, github_token=None):
    repo, owner = get_ower_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}" # this api returns the details of the PR, fro where we need the ['header']['sha']
    header = {"Authorization": f"Bearer {github_token}"} if github_token else {}

    response = requests.get(url, headers=header)
    response.raise_for_status()
    return response.json()


def fetch_file_content(repo_url, file_path, ref, github_token=None):
    repo, owner = get_ower_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={ref}"
    header = {"Authorization": f"Bearer {github_token}"} if github_token else {}
    response = requests.get(url, headers=header)
    response.raise_for_status()

    response_dict = response.json() # convert the response from json format to python dictionary
    try:
        file_content = base64.b64decode(response_dict['content']).decode()
        return file_content
    except UnicodeDecodeError:
        return None

# ================= The main function from where the pr request files will be analyzed ==================
def analyze_pr(repo_url, pr_number, github_token=None):
    github_token = github_token or os.environ.get("GITHUB_API_KEY")
    task_id = str(uuid.uuid4()) # create a UUID for each of the task

    try:
        pr_details = fetch_pr_details(repo_url, pr_number, github_token)
        head_sha = pr_details["head"]["sha"]
        
        pr_files = fetch_pr_files(repo_url, pr_number, github_token)
        
        all_analyze_results = []

        # for each file the LLM model will give a analysis result that will be stored in analyze_results array with the file name
        for file in pr_files:
            if file.get("status") == "removed":
                continue
            
            file_name = file['filename']
            raw_content = fetch_file_content(repo_url, file_name, head_sha, github_token)

            if raw_content is None:
                continue

            analyze_result = analyze_code_llm(raw_content, file_name)

            all_analyze_results.append({'file_name': file_name, 'result': analyze_result})
        
        return {'task_id': task_id, 'all_analyze_results': all_analyze_results}
    
    except Exception as e:
        print(e)
        return {'task_id': task_id, 'all_analyze_results': []}
