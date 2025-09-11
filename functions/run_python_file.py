import os
import subprocess
from config import TIMEOUT_SECONDS
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    base_path = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_path.startswith(base_path + os.sep) and target_path != base_path:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(file_path):
        return f'Error: File "{file_path}" not found.'
    if not target_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    try:
        command = ["python", target_path] + args
        result = subprocess.run(command, timeout=TIMEOUT_SECONDS, capture_output=True, text=True, check=True)
        if result.returncode != 0:
            return f"Process exited with code {result.returncode}"
        if not result.stdout and not result.stderr:
            return "No output produced."
        return f"STDOUT: {result.stdout}, STDERR: {result.stderr}"
    except subprocess.TimeoutExpired as e:
        return f"Error: executing Python file: Subprocess timed out after {TIMEOUT_SECONDS} seconds with the stdout: {e.stdout} and stderror: {e.stderror}"
    except subprocess.CalledProcessError as e:
        return f"Error: executing Python file: Subprocess failed with error {e}"
    except FileNotFoundError:
        return f"Error: executing Python file: File was not found"
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
    
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Checks if the file exists, if so, runs the python file and returns the stdout and stderr.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path that you expect the file you want to write in, is in. It will be joined with the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="The arguments you want to be included when the command is run (for the python file).",
            ),
        },
    ),
)