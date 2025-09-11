import os
from google.genai import types

def write_file(working_directory, file_path, content):
    base_path = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_path.startswith(base_path + os.sep) and target_path != base_path:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists:
        try:
            os.makedirs(target_path, exist_ok=True)
            print(f"Directory '{target_path}' created (or already existed).")
        except OSError as e:
            print(f"Error creating directory: {e}")
    try:
        with open(target_path, "w") as f:
            f.write(content)
    except Exception as e:
        return f"Error: {e}" 
    try:
        with open(target_path, "r") as f:
            text = f.read()
            if text == content:
                return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {e}" 
    
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Checks if the filepath exists, if not creates it, then writes to the file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path that you expect the file you want to write in, is in. It will be joined with the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content you want written in the file.",
            ),
        },
    ),
)