from datetime import datetime
import pandas as pd
import re

# Change paths accordingly
ORIGINAL_PLAYERS = "./data/players.csv"
NEW_TEAMS = "data/player_teams.csv"
NEW_PLAYERS = "data/players_processed.csv"
TEAMS_LIST = "data/teams_list.txt"
COUNTRIES_LIST = "data/countries_list.txt"
FULL_DATA = "data/full_data.csv"


def process_players(players: pd.DataFrame) -> pd.DataFrame:
    """
    Get more information about players from their card.
    args:
        :pd.DataFrame players - Dataframe containing original information about players
    retruns:
        :pd.DataFrame - adjusted players DataFrame
    """
    players = players.drop_duplicates()
    players["BirthCountry"] = None
    players["Age"] = None
    players["Role"] = None

    age_pattern = r"\(age (\d+)\)"

    for _, player in players.iterrows():
        country_of_birth = None
        role = None
        age = None
        # Get new columns by extracting data from PlayerCard (values are separated by ;)
        for info in player["PlayerCard"].split(";"):
            if "Country of Birth" in info:
                country_of_birth = info.replace("Country of Birth", "").strip()
            if "Role" in info:
                role = info.replace("Role", "").strip()

            match = re.search(age_pattern, info)
            # Extract the age if a match is found
            if match:
                age = match.group(1)

        player["BirthCountry"] = country_of_birth
        player["Age"] = age
        player["Role"] = role

    players["PlayerId"] = [i for i in range(len(players))]
    return players


def process_teams(players: pd.DataFrame) -> pd.DataFrame:
    """
    Get more information about teams of players from their history.
    args:
        :pd.DataFrame players - Dataframe containing original information about players
    retruns:
        :pd.DataFrame - adjusted players DataFrame
    """
    teams_df = pd.DataFrame(columns=["PlayerId", "Team", "Since", "Till"])
    team_name_pattern = r"Team (.+?) -"
    since_pattern = r"Since: (\d{4}-\d{2}-\d{2})"
    till_pattern = r"Till: (\w+)"

    for index, player in players.iterrows():
        if pd.isnull(player.TeamHistory):
            continue
        for team_info in player.TeamHistory.split(";"):
            if team_info == "":
                continue
            # Extract information about teams using re.search
            team_name_match = re.search(team_name_pattern, team_info)
            since_match = re.search(since_pattern, team_info)
            till_match = re.search(till_pattern, team_info)

            # Get the extracted information to variables
            team_name = team_name_match.group(1) if team_name_match else None
            since_date = since_match.group(1) if since_match else None
            till_info = till_match.group(1) if till_match else None

            # If "Till" is "Present", set till_date to today's date; otherwise, use the extracted value
            if pd.isnull(till_info) or till_info.lower() == "present":
                till_date = datetime.now().strftime("%Y-%m-%d")
            else:
                till_date = till_info

            if team_name is not None:
                teams_df = pd.concat(
                    [
                        teams_df,
                        pd.DataFrame(
                            {
                                "PlayerId": [player.PlayerId],
                                "Team": [team_name],
                                "Since": [since_date],
                                "Till": [till_date],
                            }
                        ),
                    ],
                    ignore_index=True,
                )

    return teams_df


def main():
    """With the usage of pandas dataframe preprocess csv file to better suit our needs."""
    players = pd.read_csv(ORIGINAL_PLAYERS, delimiter="\t")
    players = process_players(players)
    teams = process_teams(players)

    with open(TEAMS_LIST, "w") as f:
        for t in list(teams.Team.unique()):
            f.write(str(t) + "\n")

    with open(COUNTRIES_LIST, "w") as f:
        for c in list(players.BirthCountry.unique()):
            f.write(str(c) + "\n")

    # Merge teams on the players, creating unique combinations of player--their team in the csv
    merged_df = pd.merge(teams, players, on="PlayerId", how="outer")

    teams.to_csv(NEW_TEAMS, sep="\t", index=False)
    players.to_csv(NEW_PLAYERS, sep="\t", index=False)
    merged_df.to_csv(FULL_DATA, sep="\t", index=False)


main()
