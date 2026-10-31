import os
from dotenv import load_dotenv
from pathlib import Path
from groq import Groq


# load env file 
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env", override=False)

def analyze_code_llm(diff_content, file_name):
    """
    Analyzes changed lines from a pull request diff and returns JSON findings.
    """

    user_prompt = f"""
    Review the changed lines in this pull request diff based on these criteria:
    - Best practice
    - Code style and formatting issues
    - Bugs and errors
    - Performance improvement
    
    File Name: {file_name}
    Changed lines:
    {diff_content}

    Lines prefixed with "+" are additions and lines prefixed with "-" are deletions.
    The annotations give the line number in the new file for additions and the old
    file for deletions. Focus findings on added lines; use deleted lines only as context
    and do not report issues solely on deleted code.

    Return valid JSON in this structure:
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
    """
    system_prompt = "Return only valid JSON with an issues array. Do not include markdown fences."
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
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
        max_completion_tokens=2048,
        top_p=1,
    )
    
    llm_response = completion.choices[0].message.content

    return llm_response
