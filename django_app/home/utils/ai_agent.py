import os

from groq import Groq

from home.utils.env import load_env_files


load_env_files(__file__)

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
