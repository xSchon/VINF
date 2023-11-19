import re
import json
import pandas as pd

def main():
    xxx = pd.read_csv('./data/full_data.csv', delimiter='\t')

    with open('./data/parsed_countries.json', 'r') as f:
        cntr = json.load(f)

    # Convert the JSON data to a list of dictionaries
    json_list = [{'country': key, 'content': value} for key, value in cntr.items()]
    cntr = pd.DataFrame(json_list)
    
    cntr['Sports'] = None
    cntr['InfoBox'] = None
    cntr['CountryIntro'] = None
    
    sports_info_pattern = re.compile(r'===\s*Sport\s*===(.+?)==', re.DOTALL)

    # Assuming df is your DataFrame and cc is the column containing the text
    cntr['Sports'] = cntr['content'].apply(lambda x: re.search(sports_info_pattern, x).group(1).strip() if re.search(sports_info_pattern, x) else None)
    
    header_pattern = re.compile(r'(.+?)===\s*[^=]+\s*===', re.DOTALL)

    infbox = []
    cntrintro = []
    for cou in cntr.iterrows():
        cc = cou[1].content
        match = header_pattern.search(cc)
        # Check if a header is found
        if match:
            # Get all data before the header
            data_before_header = match.group(1)

        if pd.isna(cc) or not match:
            infbox.append(None)
            cntrintro.append(None)
            continue

        headers = data_before_header.split("==")[0]
        infobox_country = headers.split("'''")[0]
        print('ccc')
        country_intro = headers.split(f"'''{cou[1].country}'''")[1]
        infbox.append(infobox_country)
        cntrintro.append(country_intro)

    cntr['InfoBox'] = infbox
    cntr['CountryIntro'] = cntrintro
    
    player_with_wiki = pd.merge(xxx, cntr, left_on='BirthCountry', right_on='country', how='left')
    player_with_wiki = player_with_wiki.drop({'country', 'content'}, axis=1)
    player_with_wiki.to_csv('./data/final_data.csv', sep='\t', index=False)
    
main()