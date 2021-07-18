import requests
from bs4 import BeautifulSoup
import os
import json
import sqlite3

conn = sqlite3.connect('output.db')
c = conn.cursor()
c.execute('''CREATE TABLE modules (
	title TEXT PRIMARY KEY,
	version TEXT NOT NULL,
	updated TEXT NOT NULL,
	author TEXT NOT NULL,
	authorurl TEXT NOT NULL,
    project TEXT NOT NULL,
    manifest TEXT NOT NULL);''')


URL = "https://foundryvtt.com/packages/modules"
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find(id='package-directory')

module_list = results.find_all('li', class_='article package')

list_of_modules = []
json_of_modules = {}

for module in module_list:
    title_elem = module.find('h3', class_='article-title')
    version_elem = module.find('span', class_='tag version')
    updated_elem = module.find('span', class_='tag updated')
    author_elem = module.find('li', class_="tag author").find('a')
    author_url_elem = module.find('li', class_="tag author").find('a')['href']
    project_elem = module.find('li', class_="tag install").find('a')['href']
    if (module.find("a", {'title' : 'Manifest Installation URL'})) is not None:
        manifest_elem = module.find("a", {'title' : 'Manifest Installation URL'})['href']
    else:
        manifest_elem = "Non Existent"
    
    # For some reason, there seems to be an error as sometimes it doesn't like the update time
    updated_elem_text = updated_elem.text.replace("┬á", " ")
    
    jsonModule = {
        "title": title_elem.text.strip('\n'),
        "version": version_elem.text,
        "updated": updated_elem_text,
        "author": author_elem.text,
        "author_url": ("https://foundryvtt.com" + author_url_elem),
        "project": project_elem,
        "manifest": manifest_elem,
    }
    
    input = '''INSERT INTO MODULES(TITLE, VERSION, UPDATED, AUTHOR, AUTHORURL, PROJECT, MANIFEST) VALUES (?, ?, ?, ?, ?, ?, ?);'''
    c.execute(input, (jsonModule["title"], jsonModule["version"], jsonModule["updated"], jsonModule["author"], jsonModule["author_url"], jsonModule["project"], jsonModule["manifest"]))
    list_of_modules.append(jsonModule)

conn.commit()
