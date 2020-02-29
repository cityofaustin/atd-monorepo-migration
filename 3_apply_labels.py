"""
Tag issues with product and service labels.
"""
import csv
import json
from os import listdir
from os.path import isfile, join

import pdb
from pprint import pprint as print

from config.config import DIR_ZENHUB, DIR_LABELED, LABEL_FILE, REPO_MAP
from config.secrets import GITHUB_USER, GITHUB_PASSWORD

from _logger import get_logger

def write_issue(issue, directory):
    fname = f"{directory}/{issue['repo_name']}${issue['number']}.json"
    
    with open(fname, "w") as fout:
        logger.info(f"{issue['repo_name']} {issue['number']}")
        fout.write(json.dumps(issue))

    return True

def map_repos(labels, repo_name, repo_map):
    label = repo_map.get(repo_name)

    if label and label not in labels:
        labels.append(label)
    
    return labels


def map_labels(labels, label_lookup):
    new_labels = []

    for label in labels:
        if label in label_lookup:
            logger.info(f"{label} >> {label_lookup[label]}")
            new_labels.append(label_lookup[label])
        else:
            new_labels.append(label)

    return new_labels


def get_issue(fname):
    with open(fname, "r") as fin:
        return json.loads(fin.read())


def build_lookup(label_map):
    lookup = {}
    for row in label_map:
        label_src = row["name"]
        label_dest = row["corresponding product label"]
        lookup[label_src] = label_dest

    return lookup


def main():
    with open(LABEL_FILE, "r") as fin:
        reader = csv.DictReader(fin)
        label_map = [row for row in reader if row["action"] == "map"]

        label_lookup = build_lookup(label_map)

    fnames = [join(DIR_ZENHUB, f) for f in listdir(DIR_ZENHUB) if isfile(join(DIR_ZENHUB, f)) and f.endswith(".json")]
    
    for fname in fnames:
        issue = get_issue(fname)
        labels = issue.get("labels")
        labels = map_labels(labels, label_lookup)
        labels = map_repos(labels, issue["repo_name"], REPO_MAP)        
        issue["labels"] = labels
        write_issue(issue, DIR_LABELED)


if __name__ == "__main__":
    logger = get_logger("apply_labels")
    main()