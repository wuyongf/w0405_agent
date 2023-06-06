import logging
import os
import time
import sys
import threading
import subprocess

# Change to the desired directory
directory = "/home/nw/dev/robot-agent-v2.0/"
os.chdir(os.path.expanduser(directory))
# Run the shell script
script_path = "./run-agent.sh"
subprocess.run(["bash", script_path])