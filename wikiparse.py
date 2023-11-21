import json
import xml.etree.ElementTree as ET
import os
import re

from pyspark.sql import SparkSession


spark = SparkSession.builder \
    .appName("XMLtoJSON") \
    .config("spark.executor.memory", "16g") \
    .getOrCreate()

OUTPUT_FILE = '/data/'                                       # CHANGE ACCORDINGLY
PATH_TO_WIKIDUMP = 'data/enwiki-latest-pages-articles1.xml'  # CHANGE ACCORDINGLY
SAVE_TEAMS = OUTPUT_FILE+'/parsed_teams.json'
SAVE_COUNTRIES = OUTPUT_FILE+'/parsed_countries.json'


script_directory = os.path.dirname(__file__)
TEAMS_LIST_PATH = script_directory+'/title_lists/teams_list.txt'
COUNTRIES_LIST_PATH = script_directory+'/title_lists/countries_list.txt'


def main():
    teams_wiki = {}
    countries_wiki = {}

    with open(TEAMS_LIST_PATH, 'r') as f:
        teams_list = [line.strip() for line in f]
    
    with open(COUNTRIES_LIST_PATH, 'r') as f:
        countries_list = [line.strip() for line in f]
        
    with open(PATH_TO_WIKIDUMP, 'r') as f:
        xml_data = f.read()
    
    root = ET.fromstring(xml_data)
    for page in root.findall(".//{http://www.mediawiki.org/xml/export-0.10/}page"):
        title = page.find("{http://www.mediawiki.org/xml/export-0.10/}title").text.encode('utf-8')

        # Extracting content
        revision = page.find("{http://www.mediawiki.org/xml/export-0.10/}revision")
        text_element = revision.find("{http://www.mediawiki.org/xml/export-0.10/}text")
        content = text_element.text.encode('utf-8') if text_element is not None else "No content"
    
        # Extracting categories
        category_pattern = re.compile(r'\[\[Category:(.*?)\]\]')
        categories = category_pattern.findall(content)
    
        # Try to find team names
        for ele in categories:
            if 'esports' in ele:
                for element in teams_list: 
    	            if element == title:
    	                teams_wiki[title] = content
                        break
    	    
        for element in countries_list:
            if element == title:
                countries_wiki[title] = content
                break

    with open(SAVE_TEAMS, 'w') as outfile:
        json.dump(teams_wiki, outfile)
    
    with open(SAVE_COUNTRIES, 'w') as outfile:
        json.dump(countries_wiki, outfile)    

main()
