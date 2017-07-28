#!/usr/bin/env python

import jinja2
import os
import sys
import argparse

if __name__ == '__main__':

    # arguments
    parser = argparse.ArgumentParser(description='Performs glycopeptide search on the provided preprocessed mzML file and input database. All filepaths should be relative to the directory from which the qsub script will be submitted. The output database will be placed in the submission directory.')
    parser.add_argument('-m', '--mzml', dest='mzml', required=True, help='processed mzml file')
    parser.add_argument('-d', '--in_db', dest='in_db', required=True, help='input database file (not mzML specific)')
    parser.add_argument('-o', '--out_db', dest='out_db', required=True, help='output database file (mzML specific)')
    parser.add_argument('-i', '--id', dest='id', required=True, help='sample ID (eg. 20140905_02-restricted)')
    parser.add_argument('-s', '--source', dest='source', required=True, help='name of source dataset (eg. phil-82)')
    parser.add_argument('-e', '--email', dest='email', default='', help='email for qsub completion notification')
    args = parser.parse_args()

    # handle email
    if len(args.email) > 0:
        args.email = '#$ -m e \n#$ -M '+args.email

    template = open('search-glycopeptide.qsub.tmpl', 'r').read()
    template = jinja2.Template(template)
    script_text = template.render(processed_mzml_file=args.mzml, input_db=args.in_db, output_db=args.out_db, sample_id=args.id, source=args.source, email=args.email)
    sys.stdout.write(script_text)
