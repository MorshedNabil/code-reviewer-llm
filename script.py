# ## this file is only to check any function properly working properly or not

from urllib.parse import urlparse
import os
import requests
import base64
from pathlib import Path


# def get_ower_repo(url):
#     parsed_url = urlparse(url)
#     url_parts = parsed_url.path.strip("/").split("/")

#     if len(url_parts) >= 2:
#         owner, repo = url_parts[0], url_parts[1]
#         return repo, owner
#     return None, None

# print(get_ower_repo("https://github.com/MorshedNabil/Panic-Disorder-Detection-Website/pulls"))


# ## ==========================================
content = "ZnJvbSBmYXN0YXBpIGltcG9ydCBBUElSb3V0ZXIsIERlcGVuZHMsIEhUVFBF\neGNlcHRpb24KZnJvbSBzcWxhbGNoZW15Lm9ybSBpbXBvcnQgU2Vzc2lvbgpm\ncm9tIGFwcC5kYXRhYmFzZSBpbXBvcnQgZ2V0X2RiCmZyb20gYXBwLm1vZGVs\ncy51c2VyIGltcG9ydCBVc2VyCmZyb20gYXBwLnNjaGVtYXMudXNlciBpbXBv\ncnQgVXNlckNyZWF0ZSwgVXNlclJlc3BvbnNlLCBVc2VyTG9naW4KCnJvdXRl\nciA9IEFQSVJvdXRlcigpCgpAcm91dGVyLmdldCgiLyIpCmRlZiBnZXRfZmFy\nbWVyX2RhdGEoKToKICAgIHJldHVybiB7Im1lc3NhZ2UiOiAiRmFybWVyIGVu\nZHBvaW50cyBjb21pbmcgc29vbiJ9CgojID09PT09PT09PT09PT09PT09IGZh\ncm1lciBzaWdudXAgPT09PT09PT09PT09PT09PT0KQHJvdXRlci5wb3N0KCIv\nZmFybWVyX3NpZ251cCIsIHJlc3BvbnNlX21vZGVsPVVzZXJSZXNwb25zZSkK\nZGVmIGZhcm1lcl9zaWdudXAodXNlcl9kYXRhOiBVc2VyQ3JlYXRlLCBkYjog\nU2Vzc2lvbiA9IERlcGVuZHMoZ2V0X2RiKSk6CiAgICAjIENoZWNrIGlmIHVz\nZXIgYWxyZWFkeSBleGlzdHMgYnkgcGhvbmUgb3IgbmlkCiAgICBleGlzdGlu\nZ191c2VyID0gZGIucXVlcnkoVXNlcikuZmlsdGVyKAogICAgICAgIChVc2Vy\nLnBob25lID09IHVzZXJfZGF0YS5waG9uZSkgfCAoVXNlci5uaWQgPT0gdXNl\ncl9kYXRhLm5pZCkKICAgICkuZmlyc3QoKQogICAgCiAgICBpZiBleGlzdGlu\nZ191c2VyOgogICAgICAgIHJhaXNlIEhUVFBFeGNlcHRpb24oc3RhdHVzX2Nv\nZGU9NDAwLCBkZXRhaWw9IlVzZXIgd2l0aCB0aGlzIHBob25lIG9yIE5JRCBh\nbHJlYWR5IGV4aXN0cyIpCiAgICAKICAgIG5ld191c2VyID0gVXNlcigKICAg\nICAgICBuYW1lPXVzZXJfZGF0YS5uYW1lLAogICAgICAgIHBob25lPXVzZXJf\nZGF0YS5waG9uZSwKICAgICAgICBuaWQ9dXNlcl9kYXRhLm5pZCwKICAgICAg\nICByb2xlPXVzZXJfZGF0YS5yb2xlLCAjIEV4cGxpY2l0bHkgc2V0IHJvbGUg\nYXMgZmFybWVyCiAgICAgICAgaW1hZ2VfdXJsPXVzZXJfZGF0YS5pbWFnZV91\ncmwsCiAgICAgICAgZGl2aXNpb249dXNlcl9kYXRhLmRpdmlzaW9uLAogICAg\nICAgIGRpc3RyaWN0PXVzZXJfZGF0YS5kaXN0cmljdCwKICAgICAgICB2aWxs\nYWdlPXVzZXJfZGF0YS52aWxsYWdlCiAgICApCiAgICAKICAgIHRyeToKICAg\nICAgICBkYi5hZGQobmV3X3VzZXIpCiAgICAgICAgZGIuY29tbWl0KCkKICAg\nICAgICBkYi5yZWZyZXNoKG5ld191c2VyKQogICAgICAgIHJldHVybiBVc2Vy\nUmVzcG9uc2UubW9kZWxfdmFsaWRhdGUobmV3X3VzZXIpCiAgICBleGNlcHQg\nRXhjZXB0aW9uIGFzIGU6CiAgICAgICAgZGIucm9sbGJhY2soKQogICAgICAg\nIHJhaXNlIEhUVFBFeGNlcHRpb24oc3RhdHVzX2NvZGU9NTAwLCBkZXRhaWw9\nZiJEYXRhYmFzZSBlcnJvcjoge3N0cihlKX0iKQoKIyA9PT09PT09PT09PT09\nPT09PSBmYXJtZXIgbG9naW4gPT09PT09PT09PT09PT09PT0KQHJvdXRlci5w\nb3N0KCIvZmFybWVyX2xvZ2luIikKZGVmIGZhcm1lcl9sb2dpbih1c2VyX2Rh\ndGE6IFVzZXJMb2dpbiwgZGI6IFNlc3Npb24gPSBEZXBlbmRzKGdldF9kYikp\nOgogICAgIyBDaGVjayBpZiB1c2VyIGFscmVhZHkgZXhpc3RzIGJ5IHBob25l\nIG9yIG5pZAogICAgZXhpc3RpbmdfdXNlciA9IGRiLnF1ZXJ5KFVzZXIpLmZp\nbHRlcigKICAgICAgICAoVXNlci5waG9uZSA9PSB1c2VyX2RhdGEucGhvbmUp\nIHwgKFVzZXIubmlkID09IHVzZXJfZGF0YS5uaWQpCiAgICApLmZpcnN0KCkK\nCgogICAgaWYgbm90IGV4aXN0aW5nX3VzZXI6CiAgICAgICAgcmFpc2UgSFRU\nUEV4Y2VwdGlvbihzdGF0dXNfY29kZT00MDAsIGRldGFpbD0iSW52YWxpZCBw\naG9uZSBudW1iZXIgb3IgTklEIikKCiAgICAjIEluIGEgcmVhbCBhcHAsIHlv\ndSB3b3VsZCBnZW5lcmF0ZSBhIEpXVCB0b2tlbiBoZXJlCiAgICByZXR1cm4g\newogICAgICAgICJtZXNzYWdlIjogIkZhcm1lciBsb2dpbiBzdWNjZXNzZnVs\nIiwKICAgICAgICAidXNlcl9pZCI6IGV4aXN0aW5nX3VzZXIudXNlcl9pZCwK\nICAgICAgICAibmFtZSI6IGV4aXN0aW5nX3VzZXIubmFtZQogICAgfQ==\n"
# print(base64.b64decode(content).decode())

from groq import Groq


env_path = Path(__file__).resolve().parent / ".env"
if env_path.is_file():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def analyze_code_llm(file_content, file_name):
    user_prompt = f"""
    Analyze the code based on these criteria:
    - Best practice
    - Code style and formatting issues
    - Bugs and errors
    - Performence improvement
    
    File Name: {file_name}
    File Content: {file_content}

    Provide detail JSON output in this structure"
    {{
        "issues": [
            {{  
                "type": "<style|bugs|format|best_practice>",
                "line": <line_number>,
                "description": "<description>",
                "suggestion": "<suggestion>"           
            }}
        
        ]
    
    }}
    ```json
    """
    system_prompt = f"""
    Your evaluations writing is in text format.
    But your evaluations must be in JSON format. Here is an example of JSON response.
    ```
    {{
        "name": "main.py",
        "issues": [
        {{
            "type": "style",
            "line": 12,
            "description": "Line is too long",
            "suggesion": "Break line into multiple lines"
        }},
        {{
            "type": "bugs",
            "line": 20,
            "description": "Potential null pointer",
            "suggesion": "add null check"
        }}
        ]
    }}
    """
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        { 
            "role": "user",
            "content": user_prompt
        }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    )
    
    llm_response = completion.choices[0].message.content

    return llm_response

result = analyze_code_llm(file_content=base64.b64decode(content).decode(), file_name="farmer.py")
print(result)
