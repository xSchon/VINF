import os
import requests
import re
import time

url = "https://lol.fandom.com/wiki/League_of_Legends_Esports_Wiki"


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


def find_links(forbidden=[], searched=[]):
    pass


def drop_list_dups(arr: list) -> list:
    """Drop duplicates in a list"""
    seen = set()
    seen_add = seen.add
    return [x for x in arr if not (x in seen or seen_add(x))]


def main():
    """Main function for crawling data about League of Legends."""
    processed = load_links("processed.txt")
    toprocess = load_links("toprocess.txt")

    home_link = "https://lol.fandom.com"
    if toprocess == []:
        toprocess = ["/wiki/League_of_Legends_Esports_Wiki"]
    nonindex = process_robots()

    # Regex recognizing HREFS starting with /wiki/, which suggests leading to lol.fandom.com/wiki page
    link_pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href="(/wiki/[^"]*)"')

    for href in toprocess:
        url = f"{home_link}{href}"
        directory_path = f".{href}"
        response = requests.get(url)

        if response.status_code == 200:
            # Find and parse all of the links on page
            links = re.findall(link_pattern, response.text)

            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            with open(f"{directory_path}/page.txt", "w") as f:
                f.write(response.text)

            for link in links:
                valid = True

                # If the link was already processed or if the link is forbidden, skip it
                for nonilink in nonindex:
                    if nonilink in link:
                        valid = False

                if link in processed or link == href:
                    valid = False

                if valid:
                    toprocess.append(link)

            # Write down what links to proces in future and mark this one as processed
            toprocess = drop_list_dups(toprocess)
            toprocess = toprocess[1:]
            store_links(toprocess, "toprocess.txt")

            processed.append(href)
            store_links(processed, "processed.txt")
            print(f"Sucesfully processed page {href}")
            time.sleep(3)

        else:
            print(
                f"{url} returned response code {response.status_code}, skipping, writing to file."
            )
            with open(f"skipped.txt", "a") as f:
                f.write(url + "\n")

            toprocess = toprocess[1:]
            store_links(toprocess, "toprocess.txt")
            time.sleep(3)


main()
