import os
import requests
import re
import time

csv_header = "PlayerName\tTeamHistory\tHistoryText\tPlayerCard\tTournamentResults\tChampionsStats\n"
url = "https://lol.fandom.com/wiki/League_of_Legends_Esports_Wiki"

if not os.path.exists("./data/"):
    os.makedirs("./data/")
CSV_FILE = "./data/players.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as f:
        f.write(csv_header)


def process_robots(FILE_PATH="robots.txt"):
    """
    Read and procesess robots.txt.
    returns:
        list containing all of the forbidden pages for robots, which they shouldn't access
    """
    nonindexable = []

    with open(FILE_PATH, "r") as robots:
        dis_pattern = re.compile(r".*(?:Disallow|Noindex).*")
        agent_pattern = re.compile(r"^User-agent:.*")
        agent = "*"

        for line in robots:
            if agent_pattern.match(line):
                agent = line.split(" ")[1].strip()

            if agent == "*":  # Find patterns dissalowed or noindexed for all robots
                if dis_pattern.match(line):
                    nonindexable.append(line.split(" ")[1].strip())

    return nonindexable


def store_links(arr: list, filename: str) -> None:
    """
    Store links in an external file
    args:
        :list arr - containing all of the links to write
        :str filename - PATH to the file to save links at
    """
    with open(filename, "w") as file:
        for link in arr:
            file.write(link + "\n")


def load_links(filename: str) -> list:
    """
    Load links from file to array
    args:
        :str filename - PATH to file to retrieve links from
    retrurns:
        :list of links in the file
    """
    full_list = []
    try:
        with open(filename, "r") as file:
            for line in file:
                full_list.append(line.strip())

        return full_list
    except FileNotFoundError:
        return []


def drop_list_dups(arr: list) -> list:
    """Drop duplicates in a list"""
    seen = set()
    seen_add = seen.add
    return [x for x in arr if not (x in seen or seen_add(x))]


def get_player_teams(rows: list) -> str:
    """
    Function for parsing information about teams player played in.
    args:
        :list rows - list from the table in HTML, containing information about player's teams
    returns:
        :str - processed teams data
    """
    player_teams = ""

    cell_regex_pattern = r"<td\b[^>]*>(.*?)<\/td>"
    for row in rows:
        region, team_name, lane, time_value, since, till = "", "", "", "", "", "Present"
        cells = re.findall(cell_regex_pattern, row, re.DOTALL)
        for cell in cells:
            # Get player's teams names
            name_pattern = r"<span[^>]*><a[^>]*>(.*?)<\/a><\/span>"
            lane_pattern = r'<span\s+title="(.*?)"\s+class=".*?"'
            time_pattern = r"(\d+d|\d+yr\s*\d*mo|\d+mo\s*\d*d|\d+yr\s*\d*d)"
            region_pattern = r"<div[^>]*>(.*?)<\/div>"
            date_pattern = r"<span[^>]*>\d{4}-\d{2}-\d{2}<\/span>"

            # Get team's region
            match_region = re.search(region_pattern, cell)
            if match_region:
                rg = match_region.group(1).strip()
                if not ("ej" in rg):
                    region = rg

            # Get team's name
            name_match = re.search(name_pattern, cell)
            if name_match:
                team_name = name_match.group(1).strip()

            # Get player's lane assigments
            lane_match = re.search(lane_pattern, cell)
            if lane_match:
                lane = lane_match.group(1).strip()

            # Get player's time in the team
            match_time = re.search(time_pattern, cell)
            if match_time:
                time_value = match_time.group(1).strip()

            # Get since date and till date
            date_match = re.search(date_pattern, cell)
            # Process the match
            if date_match:
                date_string = re.search(
                    r"\d{4}-\d{2}-\d{2}", date_match.group(0)
                ).group()
                if since == "":
                    since = date_string
                else:
                    till = date_string

        if (
            team_name != ""
            or region != ""
            or lane != ""
            or since != ""
            or time_value != ""
        ):
            player_teams += f"Team {team_name} - Region: {region} , Lane: {lane} , Since: {since} , Till: {till} , Total: {time_value} ;"

    return player_teams


def get_player_card(player_card: str) -> str:
    """
    Function for processing player's data in his
    InfoCard and returning cleaner string
    """
    player_string = ""

    body_player_card_pattern = r"<tbody>.*?</tbody>"
    match_card = re.search(body_player_card_pattern, player_card, re.DOTALL)
    if match_card:  # if it's player
        player_card = match_card.group()
        pattern = r"<tr>(.*?)</tr>"
        # Get all rows and process clean text from them
        rows = re.findall(pattern, player_card, re.DOTALL)
        for row in rows:
            clean_row = re.sub("<.*?>", " ", row)
            player_string += clean_row + "; "

    player_string = " ".join(player_string.split())
    return player_string


def get_player_history(text: str) -> str:
    """
    Function for processing player's data in his
    History Tab and returning cleaner string
    """
    pattern = r'<table[^>]*class="news-table news-player-table hoverable-rows"[^>]*>.*?<tbody>(.*?)</tbody>'
    matches = re.findall(pattern, text, re.DOTALL)
    history_text = ""
    if matches:
        for _, match in enumerate(matches, start=1):
            table_text = re.sub("<[^<]+?>", " ", match)
            history_text += table_text + "; "

    history_text = " ".join(history_text.split())
    return history_text


def get_stats(text: str) -> str:
    """
    Function for processing player's data in his
    stats tab and returning cleaner string
    """
    pattern = r'<table[^>]*class="wikitable[^>]*>(.*?)<\/table>'
    match = re.search(pattern, text, re.DOTALL)

    table_text = ""
    if match:
        table_content = match.group(1)
        rows = re.findall(r"<tr>(.*?)<\/tr>", table_content, re.DOTALL)
        for row in rows:
            row_text = re.sub("<[^<]+?>", " ", row)
            row_text = " ".join(row_text.split())
            table_text += row_text + "; "
    return table_text


def regex_player(text: str, url: str) -> bool:
    """
    Use Regexes to get information about the player currently processed.
    args:
        :str text - HTML of the page
        :str url - URL to the player's page
    returns:
        :bool - True if the text contains player, False otherwise
    """
    # Box pattern - find if is player (infoboxPlayer in their table)
    box_pattern = r"(\"infoboxPlayer\")(.*)</table>"
    player_matches = re.search(box_pattern, text, re.DOTALL)
    (
        player_name,
        team_history,
        history_text,
        player_card,
        tournament_results,
        champions_stats,
    ) = ("", "", "", "", "", "")

    if player_matches:
        # Extract title
        title_pattern = r"(\".*title-main.*\">)(.*?)<\/span>"
        title_match = re.search(title_pattern, text)
        if title_match:
            player_name = title_match.group(2).strip()

        # Extract team history as a string and process
        history_table = re.search(
            r"<table\b[^>]*class=\"player-team-history\b[^>]*>(.*?)<\/table>",
            text,
            re.DOTALL,
        )
        if history_table:
            row_regex_pattern = r"<tr\b[^>]*>(.*?)<\/tr>"
            rows = re.findall(
                row_regex_pattern, history_table.group(1).strip(), re.DOTALL
            )
            team_history = get_player_teams(rows)
        else:
            team_history = ""

        # Get and process player's card
        player_card = player_matches.group(2)
        player_card = get_player_card(player_card).strip()

        history_text = get_player_history(text)

        # Extract tournament results as a string
        time.sleep(2)
        response = requests.get(f"{url}/Tournament_Results")
        if response.status_code == 200:
            tr = response.text
            tournament_results = get_stats(tr)
        else:
            tournament_results = ""

        # Extract champions played as a string
        time.sleep(2)  # SLEEP TO NOT GET BANNED
        response = requests.get(f"{url}/Statistics")
        if response.status_code == 200:
            tr = response.text
            champions_stats = get_stats(tr)
        else:
            champions_stats = ""

        # Write down all of the information about the player
        with open(CSV_FILE, "a") as players:
            players.write(
                f"{player_name}\t{team_history}\t{history_text}\t{player_card}\t{tournament_results}\t{champions_stats}\n"
            )
        return True
    else:
        return False


def players_only():
    """Main function of the program, crawling data about players"""
    # Select only player or team names from pacthed links (/wiki/OneValue)
    toprocess = load_links("toprocp.txt")
    home_link = "https://lol.fandom.com"

    player_p = r"\/wiki\/[^?/:]+$"
    # Iterate through the links and print the matches of players
    for href in toprocess:
        if re.match(player_p, href):
            url = f"{home_link}{href}"
            response = requests.get(url)
            if response.status_code == 200:
                if regex_player(response.text, url):
                    print(f"Processing player {href}")
                    with open("player_processed.txt", "a") as f:
                        f.write(href + "\n")

            time.sleep(1.5)
        toprocess = toprocess[1:]
        store_links(toprocess, "toprocp.txt")


players_only()
