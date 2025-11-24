# Open the file and upload it to temp.sh
import requests

path = "/home/platypus/photofriend/main.py"

with open(path, "r") as f:
    files = {'file': f}
    response = requests.post("https://temp.sh/", files=files)
    print(response.text)