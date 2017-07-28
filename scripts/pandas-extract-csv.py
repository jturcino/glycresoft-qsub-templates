#!/usr/bin/env python

import pandas as pd
import argparse

if __name__ == '__main__':

    # arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv', dest='csv', required=True, action='append', help='paths to csv files from which to extract n glycans')
    args = parser.parse_args()

    # get content of csv files provided
    contentlist = []
    for f in args.csv:
        content = pd.read_csv(f)
        contentlist.append(content)

    # get unique set of all glycopeptides
    glycopeptides = [ c.glycopeptide for c in contentlist ]
    glycopeptides = pd.concat(glycopeptides)
    unique_glycans = set(glycopeptides.str.extract(r"(\{.+\})", expand=False))

    # print n-glycans
    for i in unique_glycans:
        s = "{}  {}".format(i, 'n-glycan')
        print s
