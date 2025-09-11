import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file



load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

def call_function(function_call_part, verbose=False):
    name = str(function_call_part.name).strip()
    args = function_call_part.args
    args = dict(args)
    args["working_directory"] = "./calculator"
    if not name:
        print(f"Error: Function call needs the name of the function")
    if not args:
        print(f"Error: Function call needs the arguments for the function")
    if verbose:
        print(f"Calling function: {name}({args})")
    else:
        print(f" - Calling function: {name}")
    if name == "get_files_info":
        result = get_files_info(**args)
    elif name == "get_file_content":
        result = get_file_content(**args)
    elif name == "run_python_file":
        result = run_python_file(**args)
    elif name == "write_file":
        result = write_file(**args)
    else:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=name,
                        response={"error": f"Unknown function: {name}"},
                    )
                ],
            )
        
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=name,
                response={"result": result},
            )
        ],
    )    
        
def query(messages, verbose=False):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001", contents=messages, config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt)
    )
    if response.function_calls:
        arg = response.function_calls[0]
        result = call_function(arg)
        if not result.parts[0].function_response.response:
            raise Exception("Error: No response")
        if verbose:
            return f"-> {result.parts[0].function_response.response}"
        else:
            return f"{result}"

   
    


def main():
    
    if len(sys.argv) < 2:
        print("uv run main.py <query string> <optional '--verbose'>")
        sys.exit(1)
    user_prompt = str(sys.argv[1])
    messages = [types.Content(role="user",parts=[types.Part(text=user_prompt)])]
    
    if len(sys.argv) == 2:
        response = query(messages)
        
    if len(sys.argv) > 2:
        response = query(messages, verbose=True)
    
    print(response)
    
    

        
    
    
    

if __name__ == "__main__":
    main()
