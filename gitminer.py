#!/usr/bin/env python3
# coding=utf-8
__version__ = "1.0"
import argparse
import datetime
import json
import logging
import os
import sys
import time
import csv


from github import Github, GithubException
from tabulate import tabulate
from termcolor import colored

file = open("config.json", "r")
data = json.load(file)
file.close()
ACME_GITHUB_HOSTNAME = data["ACME_GITHUB_HOSTNAME"]
ACME_GITHUB_TOKEN = data["ACME_GITHUB_TOKEN"]
WORKING_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_DIR = WORKING_DIR + "/logs/"
BEGIN = time.time()
BANNER = """
**************************************************
               GITMINER:
A tool to mine useful data from Github Enterprise
**************************************************
"""
# Creates logs dir if it doesn't exist
if not os.path.isdir(LOG_DIR):
    try:
        os.mkdir(LOG_DIR)
    except Exception as e:
        print(f"[*] Could not create logs/ dir because of: {e}, exiting ...")
        sys.exit()

log = logging.getLogger()
log.setLevel(logging.INFO)

tstamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
output_file_handler = logging.FileHandler("{}git_miner_{}.log".format(LOG_DIR, tstamp))
stdout_handler = logging.StreamHandler(sys.stdout)

log.addHandler(output_file_handler)
log.addHandler(stdout_handler)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--hostname",
    dest="hostname",
    help="Hostname URL: acme",
    action="store",
    required=True,
)
parser.add_argument(
    "--org",
    dest="org_name",
    help="Organization Name(ex: Security)",
    action="store",
    required=False,
)
parser.add_argument(
    "--repo",
    dest="repo_name",
    help="Repository Name(ex: GitMiner)",
    action="store",
    required=False,
)
parser.add_argument(
    "-a",
    "--all",
    dest="all_orgs",
    help="To run in all orgs and repos, set this flag.",
    action="store_true",
    default=False,
    required=False,
)
parser.add_argument(
    "-n",
    "--noprompt",
    dest="noprompt",
    help="Do not prompt.",
    action="store_true",
    default=False,
    required=False,
)
parser.add_argument(
    "-c",
    "--csv",
    dest="csv_file",
    help="write CSV data to file",
    action="store",
    required=False,
)
parser.add_argument(
    "-j",
    "--json",
    dest="json_file",
    help="write jsonL data to file",
    action="store",
    required=False,
)

args = parser.parse_args()
hostname = args.hostname if args.hostname else None
org_name = args.org_name if args.org_name else None
repo_name = args.repo_name if args.repo_name else None
all_orgs = args.all_orgs if args.all_orgs else None
noprompt = args.noprompt if args.noprompt else None
csv_file = args.csv_file if args.csv_file else None
json_file = args.json_file if args.json_file else None


def bytesto(bytes, to, bsize=1024):
    """
    Converts bytes to a specific type of size

    Args:
        bytes (Integer): Number of Bytes to convert
        to (String): The requested size to covert to
        bsize (int, optional): Defaults to 1024.

    Returns:
        (Float): Returns a converted byte size as a Float
    """
    a = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}
    r = float(bytes)
    return bytes / (bsize ** a[to])


class GithubCli(object):
    def __init__(self, repo: str = None, org: str = None):
        self.client = None
        self.orgs = None
        self.org_name = None
        self.org = None
        self.repo = None
        self.repo_name = None
        self.repos = None
        self.languages = None
        self.contents = None
        self.language_table = None
        self.org_count = 0
        self.repo_count = 0
        self.language_dict = {}
        self.identified_languages = set()
        self.csv_file = csv_file
        self.json_file = json_file
        self.report_repos_by_org = []

    def connect(self, url, token: str):
        self.client = Github(
            base_url=f"https://{url}/api/v3", login_or_token=f"{token}"
        )

    def get_all_organizations(self):
        return self.client.get_organizations()

    def get_organization(self, org_name):
        return self.client.get_organization(org_name)

    def get_all_repos(self):
        return self.client.get_repos(self.organization)

    def get_repo(self, repo_name):
        return self.org.get_repo(repo_name)

    def get_file_contents(self):
        return self.repo.get_contents("/")

    def get_languages(self):
        return self.repo.get_languages()

    def calculate_sum(self, dict):
        """
        Calculates the sum of the values of a dict

        Args:
            dict (dict): Calculates the sum of the values of languages_dict

        Returns:
            Int: sum of the values
        """
        values = dict.values()
        return sum(values)

    def percentage(self, count, total_count):
        """
        Calculates percentage given a count and total count

        Args:
            count (Integer): # of times language appeared as core language
            total_count (Integer): total count of languages

        Returns:
            Integer: Returns the percentage as an int
        """
        percentage = 100 * float(count) / float(total_count)
        return str(int(percentage)) + "%"

    def create_table_list(self, dictionary):
        """
        Creates a table list to display results using tabulate

        Args:
            dict (dict): language dictionary

        Returns:
            List: A Nested list of languages, count and percentage
        """
        total_count = self.calculate_sum(dictionary)
        language_table = []
        for language, count in dictionary.items():
            if not language:
                language = "Empty"
            percentage = self.percentage(count, total_count=total_count)
            temp_list = [language, count, percentage]
            language_table.append(temp_list)
        language_table.sort(key=lambda language_table: language_table[1], reverse=True)
        return language_table

    def get_repo_details(self, g):
        """
        Gets all repository detailes including Org Name, Owner, Url, and Repositories and the following data:
        - Repo Name
        - Core Language
        - All languages in the repo
        - Root content files

        Args:
            g (github client): Instantiated Github client
        """
        g.repos = g.org.get_repos()

        log.info(
            f"\n{colored('Organization', color='blue', attrs=['bold', 'underline'])}: {g.org.login}"
        )
        log.info(
            f"{colored('Owner', color='blue', attrs=['bold', 'underline'])}: {g.org.email}"
        )
        log.info(
            f"{colored('Org Url', color='blue', attrs=['bold', 'underline'])}: {g.org.html_url}"
        )
        log.info(f"{colored('Repos', color='blue', attrs=['bold', 'underline'])}:")
        for repo in g.repos:
            g.repo = repo

            # TODO this duplicates get_single_repo_details?
            g.repo_count += 1
            g.languages = g.repo.get_languages()
            try:
                g.contents = g.repo.get_contents("/")
            except GithubException as e:
                log.info(f"[!] {e.args[1]['message']}")
            log.info(f" |")
            log.info(f" |- {colored(f'Repo Name', color='green')}: {g.repo.name}")
            log.info(
                f" |- {colored(f'Core Language', color='green')}: {g.repo.language}"
            )
            if g.repo.language not in g.identified_languages:
                g.identified_languages.add(g.repo.language)
                g.language_dict[g.repo.language] = 1
            else:
                g.language_dict[g.repo.language] += 1
            log.info(f" |- {colored(f'Languages:', color='green')}")
            for language, byte_size in g.languages.items():
                byte_size = bytesto(byte_size, to="k")
                log.info(f"  |")
                log.info(f"   |- {colored(f'Language: {language}', attrs=['bold'])}")
                log.info(
                    f"   |- {colored(f'Byte Size: {byte_size} KB', attrs=['bold'])}"
                )
            log.info(f" |- {colored(f'Root Content Files:', color='green')}")
            log.info(f"  |")
            for content in g.contents:
                log.info(f"   | * {colored(f'{content.path}', attrs=['bold'])}")

            _repo = {
                "org": g.org.login,
                "org_owner": g.org.email,
                "org_url": g.org.html_url,
                "repo_name": g.repo.name,
                "repo_lang": g.repo.language,
                "repo_langs": [x for x in g.languages],
                "repo_tld": [x.path for x in g.contents],
            }

            self.report_repos_by_org.append(_repo)

        log.info(
            f'{colored(f"[&] Total # of repos:", color="yellow")} {colored(str(g.repo_count), attrs=["underline", "bold"])}'
        )
        g.org_count += 1

    def get_single_repo_details(self, g):
        """
        Gets details for a single repository including Org Name, Owner, Url, and repo with the following data:
        - Repo Name
        - Core Language
        - All languages in the repo
        - Root content files

        Args:
            g (github client): Instantiated Github client
        """
        log.info(
            f"\n{colored('Organization', color='blue', attrs=['bold', 'underline'])}: {g.org.login}"
        )
        log.info(
            f"{colored('Owner', color='blue', attrs=['bold', 'underline'])}: {g.org.email}"
        )
        log.info(
            f"{colored('Org Url', color='blue', attrs=['bold', 'underline'])}: {g.org.html_url}"
        )
        log.info(f"{colored('Repos', color='blue', attrs=['bold', 'underline'])}:")
        g.repo_count += 1
        g.languages = g.repo.get_languages()
        try:
            g.contents = g.repo.get_contents("/")
        except GithubException as e:
            log.info(f"[!] {e.args[1]['message']}")
        log.info(f" |")
        log.info(f" |- {colored(f'Repo Name', color='green')}: {g.repo.name}")
        log.info(f" |- {colored(f'Core Language', color='green')}: {g.repo.language}")
        if g.repo.language not in g.identified_languages:
            g.identified_languages.add(g.repo.language)
            g.language_dict[g.repo.language] = 1
        else:
            g.language_dict[g.repo.language] += 1
        log.info(f" |- {colored(f'Languages:', color='green')}")
        for language, byte_size in g.languages.items():
            byte_size = bytesto(byte_size, to="k")
            log.info(f"  |")
            log.info(f"   |- {colored(f'Language: {language}', attrs=['bold'])}")
            log.info(f"   |- {colored(f'Byte Size: {byte_size} KB', attrs=['bold'])}")
        log.info(f" |- {colored(f'Root Content Files:', color='green')}")
        log.info(f"  |")
        for content in g.contents:
            log.info(f"   | * {colored(f'{content.path}', attrs=['bold'])}")
        log.info(
            f'{colored(f"[&] Total # of repos:", color="yellow")} {colored(str(g.repo_count), attrs=["underline", "bold"])}'
        )
        g.org_count += 1

    def print_details(self, g):
        """
        Function used to print all data gathered results.
        Prints out the total # of repos, orgs and provide a table of collected data

        Args:
            g (github client): Instantiated Github client
        """
        log.info(f"\n**************************************")
        log.info(f"[*] Grand Total number of Orgs: {g.org_count}")
        log.info(f"[*] Grand Total number of Repos: {g.repo_count}")
        log.info(f"**************************************")
        g.language_table = self.create_table_list(g.language_dict)
        log.info(
            tabulate(g.language_table, headers=["Language", "Count", "Percentage"])
        )
        END = time.time()
        log.info(f"\n\n[%] Done! Total time to run: {END - BEGIN} seconds\n")

    def write_csv(self, g):
        """
        Function used to write CSV of all data gathered results.
        Writes the total # of repos, orgs and provide a table of collected data

        Args:
            g (github client): Instantiated Github client
        """

        with open(self.csv_file, "w") as f:
            fieldnames = [
                "org",
                "org_owner",
                "org_url",
                "repo_name",
                "repo_lang",
                "repo_langs",
                "repo_tld",
            ]
            csvwriter = csv.DictWriter(f, fieldnames=fieldnames)

            csvwriter.writeheader()
            for row in self.report_repos_by_org:
                csvwriter.writerow(row)

    def write_json(self, g):
        """
        Function used to write jsonL of all data gathered results.
        Writes the total # of repos, orgs and provide a table of collected data

        Args:
            g (github client): Instantiated Github client
        """

        with open(self.json_file, "w") as f:
            for row in self.report_repos_by_org:
                f.write(json.dumps(row))


def main(hostname=hostname, all_orgs=all_orgs, org_name=org_name, repo_name=repo_name):
    log.info(
        f'{colored(text=BANNER, color="blue", on_color="on_grey", attrs=["bold"])}'
    )

    # Convert hostname to lowercase to ensure proper input
    hostname = hostname.lower()

    # Set the proper hostname based on '--hostname' argument flag provided
    if hostname == "acme":
        running_url = ACME_GITHUB_HOSTNAME
        running_token = ACME_GITHUB_TOKEN
    else:
        log.error("[.] Please set valid hostname flag(ex: acme) and try again")
        log.error("[*] Exiting...\n")
        sys.exit()

    if not noprompt:
        a = input(
            colored(
                text=f'[.] Are you sure you want to run this script in {colored(running_url, color="white", attrs=["bold", "underline"])}: (y/n)\n  > ',
                color="green",
            )
        )

        if a.lower() == "y":
            log.info(colored(f"\n[.] Using: {running_url}", attrs=["bold"]))
        else:
            log.error("[*] Re-run script again with desired Hostname")
            sys.exit()

    # Instantiate Github Client
    try:
        g = GithubCli()
        g.connect(running_url, running_token)
    except Exception as e:
        print(f" * [E] Exception: {e}")
        exit(3)
    # if --all flags is set, this will run on all orgs and repos
    if all_orgs and not hostname:
        log.error("[!] Please enter a hostname and try again!")
    elif all_orgs and hostname:
        if not noprompt:
            a = input(
                colored(
                    text=f"[.] Are you sure you want to run this script for all orgs: (y/n)\n  > ",
                    color="red",
                )
            )
            if a != "y":
                log.info(f"[!] Please re-run script again. \n Exiting...")
                sys.exit()

        # Get all organizations in Github
        g.orgs = g.get_all_organizations()
        # For each org, we will get different data points that will be useful
        for org in g.orgs:
            g.org = org
            try:
                g.get_repo_details(g)
            except Exception as e:
                log.error(f"[!] Could not iterate because of: {e}")
                continue
        g.print_details(g)
        if csv_file:
            g.write_csv(g)
        if json_file:
            g.write_json(g)

    # if --all flag is not provided, this will run
    elif org_name and not repo_name and not all_orgs:
        g.org_name = org_name
        log.info(
            colored(
                f"\n[.] Finding data for only ONE Org: {g.org_name}", attrs=["bold"]
            )
        )
        try:
            g.org = g.get_organization(g.org_name)
        except GithubException as e:
            if "Not Found" == e.args[1]["message"]:
                log.error(
                    f"\n[!] 404 - Organization: {g.org_name} was NOT found. Re-run script and try again\n[%] Exiting..."
                )
                sys.exit()
            else:
                log.error(f"[!] Could not get Organization because of: {e}")
        g.get_repo_details(g)
        g.print_details(g)

        if csv_file:
            g.write_csv(g)
        if json_file:
            g.write_json(g)

    elif org_name and repo_name:
        g.org_name = org_name
        try:
            g.org = g.get_organization(g.org_name)
        except GithubException as e:
            if "Not Found" == e.args[1]["message"]:
                log.error(
                    f"\n[!] 404 - Organization: {g.org_name} was NOT found. Re-run script and try again\n[%] Exiting..."
                )
                sys.exit()
            else:
                log.error(
                    f"[!] Could not get Organization: {g.org_name} because of: {e}\n[%] Exiting..."
                )
        try:
            g.repo = g.get_repo(repo_name)
        except GithubException as e:
            if "Not Found" == e.args[1]["message"]:
                log.error(
                    f"\n[!] 404 - Repository: {repo_name} was NOT found. Re-run script and try again\n[%] Exiting..."
                )
                sys.exit()
            else:
                log.error(
                    f"[!] Could not get Organization because of: {e}\n[%] Exiting..."
                )
        g.get_single_repo_details(g)
        g.print_details(g)
        if csv_file:
            g.write_csv(g)
        if json_file:
            g.write_json(g)

    else:
        log.error(
            colored(
                f"\n[!] Missing one or more args. Try again. \n",
                color="red",
                attrs=["bold"],
            )
        )
        parser.print_help()
        sys.exit()


if __name__ == "__main__":
    try:
        main(
            hostname=hostname, all_orgs=all_orgs, org_name=org_name, repo_name=repo_name
        )
    except Exception as e:
        END = time.time()
        log.error("\n[!] ERROR encountered because of: {}".format(e))
        log.exception("\n")
        log.error(f"[%] Exiting... Time Spent: {END - BEGIN} seconds")
        exit(0)
