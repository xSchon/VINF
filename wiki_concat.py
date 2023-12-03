import re
import json
import pandas as pd


def main():
    """
    Merge data downloaded via regex search and data from wikipedia into one csv (tsv)
    """
    original_data = pd.read_csv("./data/full_data.csv", delimiter="\t")

    with open("./data/parsed_countries.json", "r") as f:
        cntr = json.load(f)

    # Convert the JSON wiki data to a list of dictionaries
    json_list = [{"country": key, "content": value} for key, value in cntr.items()]
    cntr = pd.DataFrame(json_list)

    cntr["Sports"] = None
    cntr["InfoBox"] = None
    cntr["CountryIntro"] = None

    sports_info_pattern = re.compile(r"===\s*Sport\s*===(.+?)==", re.DOTALL)

    # Assuming df is your DataFrame and cc is the column containing the text
    cntr["Sports"] = cntr["content"].apply(
        lambda x: re.search(sports_info_pattern, x).group(1).strip()
        if re.search(sports_info_pattern, x)
        else None
    )

    header_pattern = re.compile(r"(.+?)===\s*[^=]+\s*===", re.DOTALL)

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

        # Process information about data further and save only important parts
        headers = data_before_header.split("==")[0]
        infobox_country = headers.split("'''")[0]
        country_intro = headers.split(f"'''{cou[1].country}'''")[1]
        infbox.append(infobox_country)
        cntrintro.append(country_intro)

    # Create columns with information about countries
    cntr["InfoBox"] = infbox
    cntr["CountryIntro"] = cntrintro

    # Merge
    player_with_wiki = pd.merge(
        original_data, cntr, left_on="BirthCountry", right_on="country", how="left"
    )
    player_with_wiki = player_with_wiki.drop({"country", "content"}, axis=1)
    player_with_wiki.to_csv("./data/final_data.csv", sep="\t", index=False)


main()
