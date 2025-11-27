import os
import subprocess

# Run the API server
if __name__ == "__main__":
    command = f"python {os.path.join(os.getcwd(), 'nyx_api', 'api.py')}"
    subprocess.run(command, shell=True)
