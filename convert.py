import base64
import sys

# Check if the token is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python convert.py <github_token>")
    sys.exit(1)

# Your GitHub token from command-line argument
github_token = sys.argv[1]

# Base64 encode the GitHub token
base64_bytes = base64.b64encode(github_token.encode('ascii'))
git_data = base64_bytes.decode('ascii')

print("encoded git_data:", git_data)