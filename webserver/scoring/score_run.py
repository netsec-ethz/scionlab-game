"""Score the results of one run of the VISCON HACKATHON.

Takes goals and results as arguments and outputs a score for each team.
"""
import csv
from argparse import ArgumentParser
from collections import defaultdict


def load_goals(filename):
    goals = defaultdict(dict)
    src_team = {}
    with open(filename, 'r') as infile:
        reader = csv.reader(infile)
        for row in reader:
            goals[row[1]][row[2]] = int(row[3])
            src_team[row[1]] = row[0]

    return goals, src_team


def load_results(filename):
    res = defaultdict(dict)
    with open(filename, 'r') as infile:
        reader = csv.reader(infile)
        for row in reader:
            res[row[0]][row[1]] = int(row[2])

    return res


def score_run(goals, results):
    scores = defaultdict(list)

    for goal_src in goals:
        for goal_dst in goals[goal_src]:
            if goal_src in results and goal_dst in results[goal_src]:
                achieved = results[goal_src][goal_dst]
                goal = goals[goal_src][goal_dst]
                score = min(1.0, achieved / goal)
                scores[goal_src].append(score)
            else:
                scores[goal_src].append(0.0)
    avg = {}
    for src in scores:
        avg[src] = sum(scores[src]) / len(scores[src])
    return avg


def write_scores(src_team, scores, out):
    with open(out, 'w') as outfile:
        writer = csv.writer(outfile)

        for src, score in scores.items():
            writer.writerow([src_team[src], src, score])


def main():
    parser = ArgumentParser()
    parser.add_argument("goals", type=str, help="Path to goals csv file.")
    parser.add_argument("results", type=str,
                        help="Path to the csv file of the results.")
    parser.add_argument("--out", type=str, help="Path to write results.",
                        default="scores.csv")

    args = parser.parse_args()

    goals, src_team = load_goals(args.goals)
    results = load_results(args.results)

    scores = score_run(goals, results)

    write_scores(src_team, scores, args.out)


if __name__ == '__main__':
    main()
