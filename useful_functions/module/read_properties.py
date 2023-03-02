import configparser
import os
import sys

# file_dir = os.path.dirname(__file__)
# print('path:', file_dir)
# sys.path.append(file_dir)

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the properties file
config.read('./config.properties')

# Get the values from the properties file
host = config.get('database', 'host')
port = config.get('database', 'port')
username = config.get('database', 'username')
password = config.get('database', 'password')

# Print the values
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Username: {username}")
print(f"Password: {password}")