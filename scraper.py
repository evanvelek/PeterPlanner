from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor

# Seed URL: https://catalogue.uci.edu/undergraduatedegrees/
SEED_URL = "https://catalogue.uci.edu/undergraduatedegrees/"

# Must remember the following:
# 1. All will be doubled because of two organizational systems
# SOLUTION: Hashing
# 2. There are links that are NOT requirement pages
# 3. Must store majors and minors separately
# Separate Hashes
HEADER = {'User-Agent': 'Mozilla/5.0'}


def extract_majors_and_minors():

    url_info = requests.get(SEED_URL, headers=HEADER)
    url_info.raise_for_status()

    soup = BeautifulSoup(url_info.content, 'html.parser')

    inside_div = soup.find('div', {'id': "textcontainer", 'class': "page_content"})

    links = inside_div.find_all('a')

    majors = {}
    minors = {}

    for link in links:
        href = link.get('href')
        text = link.get_text(strip=True)
        if not href:
            continue

        if "Minor" in text:  
            minors[text] = href
        else:
            majors[text] = href
    
    return majors, minors

def get_reqs(url):
    url_info = requests.get(url, headers=HEADER)
    url_info.raise_for_status()

    soup = BeautifulSoup(url_info.content, 'html.parser')
    reqs = []

    course_table = soup.find('table', class_="sc_courselist")
    rows = course_table.find_all('tr')

    with ThreadPoolExecutor(max_workers=10) as executor:
        reqs = list(executor.map(process_row, rows))
    return reqs
    
def process_row(row):
    code_cell = row.find('td', class_="codecol")
    if code_cell:
        code = code_cell.get_text(strip=True)
        a_tag = code_cell.find('a')
        if a_tag:
            desc_href = a_tag.get('href')
            prereqs = get_prereqs(desc_href)
            return({'code': code, 'description': prereqs})

def get_prereqs(desc_href):
    desc_url_info = requests.get("https://catalogue.uci.edu" + desc_href, headers=HEADER)
    desc_url_info.raise_for_status()
    soup = BeautifulSoup(desc_url_info.content, 'html.parser')
    inside_div = soup.find('div', {'id': 'fssearchresults', 'class':'searchresults'})
    prereqs = []
    links = inside_div.find_all('p')
    for link in links:
        text = link.get_text(strip=True)
        if 'prerequisite' in text.lower():
            atags = link.find_all('a')
            for atag in atags:
                prereqs.append(atag.get_text().replace('\xa0', " "))
    return prereqs

if __name__ == '__main__':
    #print(extract_majors_and_minors())
    example_url = "https://catalogue.uci.edu/schoolofphysicalsciences/departmentofphysicsandastronomy/physics_bs/#requirementstext"
    courses = get_reqs(example_url)
    for course in courses:
        if course is None:
            continue
        if course['code'] is None:
            course['code'] = "None"
        if course['description'] is None:
            course['description'] = "None"
        print(f"Code: {course['code']}, Description: {course['description']}")