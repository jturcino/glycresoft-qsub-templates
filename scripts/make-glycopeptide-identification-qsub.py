#!/usr/bin/env python

import jinja2
import os
import sys
import argparse

if __name__ == '__main__':

    # arguments
    parser = argparse.ArgumentParser(description='Finds all glycans in provided database and build csv file. All filepaths should be relative to the directory from which the qsub script will be submitted. The output csv file will be placed in the submission directory.')
    parser.add_argument('-d', '--db', dest='db', required=True, help='input database file (mzML specific)')
    parser.add_argument('-c', '--csv', dest='csv', required=True, help='output csv file of glycans')
    parser.add_argument('-i', '--id', dest='id', required=True, help='sample ID (eg. 20140905_02-restricted)')
    parser.add_argument('-s', '--source', dest='source', required=True, help='name of source dataset (eg. phil-82)')
    parser.add_argument('-e', '--email', dest='email', default='', help='email for qsub completion notification')
    args = parser.parse_args()

    # handle email
    if len(args.email) > 0:
        args.email = '#$ -m e \n#$ -M '+args.email

    template = open('templates/glycopeptide-identification.qsub.tmpl', 'r').read()
    template = jinja2.Template(template)
    script_text = template.render(db=args.db, csv=args.csv, sample_id=args.id, source=args.source, email=args.email)
    sys.stdout.write(script_text)
