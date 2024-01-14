import os
import subprocess
import threading

files = [
    "nyx_api/api.py",
    "discord_bot/bot.py",
]  # List of files to be executed

def run_script(file):
    command = f"python {os.getcwd()}/{file}"  # Command to execute python files
    subprocess.Popen(command, shell=True)

# Create a list to hold the thread objects
threads = []

# Start a thread for each file execution
for file in files:
    thread = threading.Thread(target=run_script, args=(file,))
    threads.append(thread)
    thread.start()

# Keep the main thread alive
while True:
    pass
