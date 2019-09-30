"""Utilities for the management of webserver directories."""
import csv
import datetime
import os
from hashlib import sha256
from shutil import rmtree, copyfile

NUM_ROUNDS = 2
DST_PER_ROUND = 3

# Directory structure
TEAMS_DIR = "teams/"
ROUNDS_DIR = "rounds/"
CONFIGS_DIR = "configs/"
INFRASTRUCTURE_DIR = "infrastructure/"
SOURCE_SUBDIR = "source/"
SINK_SUBDIR = "sink/"
LOGS_SUBDIR = "logs/"
CODE_SUBDIR = "code/"
CUR_ROUND = "cur-round"

LOGNAME = "log"

TEAMS = os.path.join(CONFIGS_DIR, "teams_ids.csv")
SOURCES = os.path.join(INFRASTRUCTURE_DIR, "src_addr")
DESTINATIONS = os.path.join(INFRASTRUCTURE_DIR, "dst_addr.csv")
CUR_ROUND_DIR = os.path.join(ROUNDS_DIR, CUR_ROUND)

SECRET = os.getenv('SECRET', default="")


def team_id(instring, length=6):
    return str(sha256(bytes(instring + SECRET, 'ascii')).hexdigest())[:length]


def teams_from_dir():
    """Read all the team names from the folders and generate team IDs."""
    teams = os.listdir(TEAMS_DIR)
    team_ids = dict(zip(list(map(team_id, teams)), teams))
    return teams, team_ids


def cleanup_dir(dir):
    """Remove all the contents in the directory"""
    if os.path.exists(dir):
        rmtree(dir)
    os.makedirs(dir)


def most_recent_timestamp(dir):
    """Returns the file with the most recent timestamp in the directory."""
    most_recent = datetime.datetime.min
    file = None
    for cur in os.listdir(dir):
        timestr = cur.split("-", maxsplit=1)[0]
        cur_time = datetime.datetime.strptime(timestr, '%y%m%d%H%M%S')
        if cur_time > most_recent:
            most_recent = cur_time
            file = cur
    return file


def check_teamid(teamid, team_ids):
    if teamid in team_ids:
        return True
    return False


def prepare_round():
    """Put the most recent code for each team in the appropriate folder.

    Round numbers start from 0.
    """
    last_round = get_last_round_num()
    cur_round = last_round + 1

    # Populate the cur-round folder with source/ and sink/ folders
    os.mkdir(CUR_ROUND_DIR)
    os.mkdir(os.path.join(CUR_ROUND_DIR, "source"))
    os.mkdir(os.path.join(CUR_ROUND_DIR, "sink"))

    # Get the config with the teamname-source mappings.
    config_name = os.path.join(CONFIGS_DIR, f"config_round_{cur_round}.csv")
    with open(config_name, 'r') as infile:
        reader = csv.reader(infile)
        for row in reader:
            move_code_to_source(row[0], row[1])


def move_code_to_source(teamname, source):
    """Copy the most recently submitted code to the appropriate source dir.

    The sumbmitted code for a team will then be:

        ./rounds/cur-round/source/<source machine addr>/<teamname>.py

    The <teamname>.py file is the runnable file.
    """
    team_code_dir = os.path.join(TEAMS_DIR, teamname, CODE_SUBDIR)
    recent_code = most_recent_timestamp(team_code_dir)
    if recent_code is not None:
        # Copy the file over to the appropriate source
        if not os.path.exists(os.path.join(CUR_ROUND_DIR,
                                           SOURCE_SUBDIR,
                                           source)):
            os.makedirs(os.path.join(CUR_ROUND_DIR, SOURCE_SUBDIR, source))
        dst = os.path.join(CUR_ROUND_DIR,
                           SOURCE_SUBDIR,
                           source,
                           f"{teamname}.py")
        copyfile(os.path.join(team_code_dir, recent_code), dst)


def get_last_round_num():
    round_names = os.listdir(ROUNDS_DIR)
    if not round_names:
        return -1
    cur_max = -1
    for name in round_names:
        if name != "cur-round":
            print(name)
            round_num = int(name.split("-")[1])  # Round folders  `round-N`
            cur_max = max(cur_max, round_num)
    return cur_max


def finish_round():
    """Clean up the folders at the end of the round.

    After round N, the cur-round folder is renamed to round-N.
    """
    last_round = get_last_round_num()
    cur_round = last_round + 1
    round_dir = os.path.join("rounds", f"round-{cur_round}")
    os.rename(CUR_ROUND_DIR, round_dir)
    src_team = machine_to_team(cur_round)

    from pprint import pprint
    pprint(src_team)

    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")

    for cur_src in os.listdir(os.path.join(round_dir, SOURCE_SUBDIR)):
        team = src_team[cur_src]
        log_name = f"{timestamp}_log"
        dst_path = os.path.join(TEAMS_DIR, team, LOGS_SUBDIR, log_name)

        copyfile(os.path.join(round_dir, SOURCE_SUBDIR, cur_src, LOGNAME),
                 dst_path)


def machine_to_team(cur_round):
    """Compute the map from teams to machines."""
    # Get the config with the teamname-source mappings.
    config_name = f"configs/config_round_{cur_round}.csv"
    machine_team = {}
    with open(config_name, 'r') as infile:
        reader = csv.reader(infile)
        for row in reader:
            machine_team[row[1]] = row[0]
    return machine_team