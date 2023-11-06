import requests
import re

print("Hello World!")

url = 'https://lol.fandom.com/wiki/2023_Season'
url = 'https://lol.fandom.com/wiki/League_of_Legends_Esports_Wiki'

link_pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href="([^"]*\/wiki\/[^"]*)"')
response = requests.get(url)	
links = re.findall(link_pattern, response.text)

# Printing the extracted links
for link in links:
    if link == 'a':
    	print('b')
    
    print(link)



"""
forbidden_links = []
with open("robots.txt", "r") as file:
    for line in file.readlines():
    	print(line)
    	if 'Noindex' in line or 'Disallow' in line:
    	    forbidden_links.append(line.split(' ')[2])

link_pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href="([^"]*\/wiki\/[^"]*)"')

links = re.findall(link_pattern, response.text)

# Printing the extracted links
for link in links:
    if link == 'a':
    	print('b')
    print(link)

"""
file_content = """
Noindex: /wiki/Special:
Noindex: /wiki/User_talk:
Noindex: /wiki/Template:
Noindex: /wiki/Template_talk:
Noindex: /wiki/Help:
Noindex: /wiki/User:
Noindex: /wiki/UserProfile:
Disallow: /wiki/Special:
Disallow: /wiki/User_talk:
Disallow: /wiki/Template:
Disallow: /wiki/Template_talk:
Disallow: /wiki/Help:
Disallow: /wiki/User:
Disallow: /wiki/UserProfile:
Disallow: /FanLabWikiBar
"""
file_content = """
Noindex: /wiki/Special:
Noindex: /wiki/User_talk:
Noindex: /wiki/Template:
Noindex: /wiki/Template_talk:
Noindex: /wiki/Help:
Noindex: /wiki/User:
Noindex: /wiki/UserProfile:
Disallow: /wiki/Special:
Disallow: /wiki/User_talk:
Disallow: /wiki/Template:
Disallow: /wiki/Template_talk:
Disallow: /wiki/Help:
Disallow: /wiki/User:
Disallow: /wiki/UserProfile:
"""

# Extracting the disallowed and noindexed paths from the file content
disallowed_paths = re.findall(r'Disallow: (.*)', file_content)
noindex_paths = re.findall(r'Noindex: (.*)', file_content)

# Creating regex patterns for disallowed and noindexed paths
disallowed_pattern = '|'.join([re.escape(path.strip()) for path in disallowed_paths])
noindex_pattern = '|'.join([re.escape(path.strip()) for path in noindex_paths])

# Regex pattern for hrefs excluding the specified paths
link_pattern = re.compile(fr'<a\s+(?:[^>]*?\s+)?href="(?!.*({disallowed_pattern}|{noindex_pattern})).*"')

# Extracting the disallowed and noindexed paths from the file content
disallowed_paths = re.findall(r'Disallow: (.*)', file_content)
noindex_paths = re.findall(r'Noindex: (.*)', file_content)

# Creating regex patterns for disallowed and noindexed paths
disallowed_pattern = '|'.join([re.escape(path.strip()) for path in disallowed_paths])
noindex_pattern = '|'.join([re.escape(path.strip()) for path in noindex_paths])

# Regex pattern for hrefs excluding the specified paths
link_pattern = re.compile(fr'<a\s+(?:[^>]*?\s+)?href="(?!.*({disallowed_pattern}|{noindex_pattern})).*"')


links = re.findall(link_pattern, response.text)

# Printing the extracted links
for link in links:
    print(link)


print(response.status_code)
#print(response.text)
