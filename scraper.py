from bs4 import BeautifulSoup
import requests

# Seed URL: https://catalogue.uci.edu/undergraduatedegrees/
SEED_URL = "https://catalogue.uci.edu/undergraduatedegrees/"

# Must remember the following:
# 1. All will be doubled because of two organizational systems
# SOLUTION: Hashing
# 2. There are links that are NOT requirement pages
# 3. Must store majors and minors separately
# Separate Hashes
HEADER = {'User-Agent': 'Mozilla/5.0'}


def extract_majors():

    url_info = requests.get(SEED_URL, HEADER)
    url_info.raise_for_status()

    soup = BeautifulSoup(url_info.content, 'html.parser')

    inside_div = soup.find('div', {'id': "textcontainer", 'class': "page_content"})

    links = inside_div.find_all('a')

    anchored_links = {}

    for link in links:
        href = link.get('href')
        text = link.get_text(strip=True)
        anchored_links[text] = href
    
    return anchored_links

if __name__ == '__main__':
    print(extract_majors())








