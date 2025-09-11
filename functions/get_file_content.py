import os
from config import MAX_CHARS
from google.genai import types

def get_file_content(working_directory, file_path):
    base_path = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_path.startswith(base_path + os.sep) and target_path != base_path:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    try:
        with open(target_path, "r") as f:
            content = f.read()
            if len(content) > MAX_CHARS:
                content = content[:MAX_CHARS] + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return content
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
    except Exception as e:
        return f"Error: {e}" 
    
    
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Checks if the filepath exists, if it does, returns the content of the file (at maximum of 10000 chars).",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path that you expect the file you want to write in, is in. It will be joined with the working directory.",
            ),
        },
    ),
)