import os
from dotenv import load_dotenv
from google import genai
import sys
import time
from google.genai import types
from google.genai.errors import ClientError
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from config import MAX_FUNCTION_CALLS



load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# Define functions that the model can call
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# Configure client and system prompt

client = genai.Client(api_key=api_key)
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.

Always list the files first, then read ALL the file contents, then look for the bug, then, if considering to fix the code, check if you're intending to rewrite an entire file. If so, rethink again. There is a bug, that is all you need to fix, you don't have to rewrite the ENTIRE thing.
"""



def call_function(function_call_part):
    name = str(function_call_part.name).strip()
    args = function_call_part.args
    args = dict(args)
    args["working_directory"] = "./calculator"
    if not name:
        print(f"Error: Function call needs the name of the function")
    if not args:
        print(f"Error: Function call needs the arguments for the function")

    print(f"Model: I want to call {name}")
    if name == "get_files_info":
        result = get_files_info(**args)
    elif name == "get_file_content":
        result = get_file_content(**args)
    elif name == "run_python_file":
        result = run_python_file(**args)
    elif name == "write_file":
        result = write_file(**args)
    else:
            return {"error": f"Unknown function: {name}"}
        
    return {"result": result}



def generate_content(messages):
    had_function_call = False
    # Pass messages
    try:
        response = client.models.generate_content(
        model="gemini-2.0-flash-001", contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt)
    )
        
    except Exception as e:
        raise

    # Check the candidate's response and add content to messages list
    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)
            for part in candidate.content.parts:
                if part.function_call:
                    had_function_call = True
                    function_call_part = part.function_call
                    function_responses = call_function(function_call_part)
                    # convert function responses to types.Content and add content to messages list
                    messages.append(types.Content(
                    role="tool",
                    parts=[
                        types.Part.from_function_response(
                            name=function_call_part.name,
                            response=function_responses
                        )
                    ]
                    ))
                    print(f"Tool: Here's the result of {function_call_part.name}: \n{function_responses.get('result')}")
                if part.text:
                    if candidate.content.role == "model":
                        print(f"Model: {part.text}")
    return response, had_function_call



def main():
    call_count = 0
    if len(sys.argv) < 2:
        print("uv run main.py <query string>")
        sys.exit(1)
    
    # Define the user prompt
    user_prompt = str(sys.argv[1]) 
    print(f"User: {user_prompt}")
    messages = [types.Content(role="user",parts=[types.Part(text=user_prompt)])]
    
    
    # Send request until response.text is made or max requests reached (20), in a try except block
    while call_count < MAX_FUNCTION_CALLS:
        try:
            response, had_function_call = generate_content(messages)
            if not had_function_call and response.text:
                break
            call_count += 1
            continue
        except ClientError as e:
                # rate limit handling
            if getattr(e, "status_code", None) == 429:
                # back off briefly, then continue or break if you prefer
                time.sleep(2)
                continue
            print(f"API error: {e}")
            break
        except Exception as e:
            raise Exception("Error: {e}")
            break
        
    

if __name__ == "__main__":
    main()
