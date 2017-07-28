#!/usr/bin/env python

import jinja2
import os
import sys
import argparse

if __name__ == '__main__':

    # arguments
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--csv', dest='csv', required=True, action='append', help='path to CSV file')
    parser.add_argument('-s', '--source', dest='source', required=True, help='name of source dataset (eg. phil-82)')
    parser.add_argument('-o', '--outfile', dest='outfile', default='nglycans.txt', help='name of output file')
    parser.add_argument('-e', '--email', dest='email', default='', help='email for qsub completion notification')
    args = parser.parse_args()

    # THE DEFINING PANDAS SCRIPT PATH VARIABLE
    pandas='/projectnb/glyco-ms/data/brite_2017/qsub_templates/pandas-extract-csv.py'

    # handle email
    if len(args.email) > 0:
        args.email = '#$ -m e \n#$ -M '+args.email

    # turn args.csv list into space-separated string
    csvs = ' '.join(args.csv)

    template = open('consolidate-glycans.qsub.tmpl', 'r').read()
    template = jinja2.Template(template)
    script_text = template.render(dataset=args.source, pandas=pandas, nglycans=args.outfile, csvs=csvs, email=args.email)
    sys.stdout.write(script_text)
