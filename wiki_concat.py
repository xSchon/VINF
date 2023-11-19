import json
import pandas as pd

def main():
    all_data = pd.read_csv('./data/full_data.csv', delimiter='\t')

    with open('./data/parsed_countries.json', 'r') as f:
        cntr = json.load(f)

    # Convert the JSON data to a list of dictionaries
    json_list = [{'country': key, 'content': value} for key, value in cntr.items()]
    cntr = pd.DataFrame(json_list)

    player_with_wiki = pd.merge(all_data, cntr, left_on='BirthCountry', right_on='country', how='left')

    player_with_wiki.to_csv('./data/final_data.csv', sep='\t', index=False)
    
main()