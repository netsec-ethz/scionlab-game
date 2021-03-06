"""Generate the configs for each run of the VISCON HACKATHON."""

import csv
import random
from argparse import ArgumentParser
from os import path


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-t", "--teams", type=str,
                        help="Path to file with team names")
    parser.add_argument("-s", "--sources", type=str,
                        help="Path to file with source SCION addresses")
    parser.add_argument("-d", "--destinations", type=str,
                        help="Path to file with SCION destination addresses "
                             "(sinks).")
    parser.add_argument("-r", "--rounds", type=int,
                        help="Number of rounds the game will be played.")
    parser.add_argument("-o", "--out", type=str,
                        help="Output folder for config files.")
    parser.add_argument("--dst_team", type=int, default=3,
                        help="The number of destinations each team has in each "
                             "round. Defaults to 3.")

    args = parser.parse_args()
    return args


def read_teamnames(filename):
    with open(filename, 'r') as infile:
        reader = csv.reader(infile)
        t = [r for r in reader]
    teamnames, team_ids = zip(*t)
    return teamnames, team_ids


def read_addr(filename):
    with open(filename, 'r') as infile:
        data = csv.reader(infile)
        data = [a for a in data]
    target = [d[0].strip() for d in data]
    size = [int(d[1].strip()) for d in data]
    return target, size


def generate_config(teams, src_addr, dst_addr, src_size, dst_size, dst_team):
    idxs = list(range(len(src_addr)))
    random_idx = random.sample(idxs, k=len(teams))
    select_src = [src_addr[i] for i in random_idx]
    select_src_sizes = [src_size[i] for i in random_idx]

    print(select_src)
    print(select_src_sizes)

    round_src = []
    round_dst = []
    round_msg_size = []
    round_teams = []

    for idx, team in enumerate(teams):
        round_teams += dst_team * [team]
        round_src += dst_team * [select_src[idx]]
        idxs_dst = random.sample(range(len(dst_addr)), dst_team)
        round_dst += [dst_addr[i] for i in idxs_dst]
        src_msg_size = select_src_sizes[idx]
        dst_msg_size = [dst_size[i] for i in idxs_dst]
        round_msg_size += [min(src_msg_size, a) for a in dst_msg_size]

    result = {
        'teams': round_teams,
        'src': round_src,
        'dst': round_dst,
        'size': round_msg_size
    }

    return result


def generate_all_configs(rounds, teams, src_addr, dst_addr, src_size, dst_size,
                         dst_team):
    confs = []
    for round in range(rounds):
        config = generate_config(teams, src_addr, dst_addr, src_size, dst_size,
                                 dst_team)
        confs.append(config)
    return confs


def write_configs(configs, filename):
    if not isinstance(configs, list):
        configs = [configs]

    for cur, config in enumerate(configs):
        outname = path.join(filename, f"config_round_{cur}.csv")
        with open(outname, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(zip(*config.values()))


def main():
    random.seed(42)

    args = parse_args()
    teams, team_ids = read_teamnames(args.teams)
    src_addr, src_size = read_addr(args.sources)
    dst_addr, dst_size = read_addr(args.destinations)

    print("VISCON HACKATON CONFIG GENERATOR")
    print("There are:")
    print(f"   - {len(teams)} teams;")
    print(f"   - {len(src_addr)} source addresses;")
    print(f"   - {len(dst_addr)} destination (sink) addresses;")
    print(f"   - {args.dst_team} destinationd for each team, each round;")
    print(f"   - {args.rounds} rounds to be played.")
    print(f"The output will be saved in {args.out}.")

    if len(teams) > len(src_addr):
        raise ValueError("There are more teams than source IPs!")

    confs = generate_all_configs(args.rounds, teams, src_addr, dst_addr,
                                 src_size, dst_size, args.dst_team)
    write_configs(confs, args.out)


if __name__ == "__main__":
    main()
