#!/usr/bin/env python

import jinja2
import os
import sys
import argparse

if __name__ == '__main__':

    # arguments
    parser = argparse.ArgumentParser(description='Make mzML preprocessing qsub script. All filepaths should be relative to the directory from which the qsub script will be submitted. The output will be written to ./preprocess/{ID}.preprocessed.mzML')
    parser.add_argument('-m', '--mzml', dest='mzml', required=True, help='path to unprocessed mzML file')
    parser.add_argument('-i', '--id', dest='id', required=True, help='sample ID (eg. 20140905_02)')
    parser.add_argument('-s', '--source', dest='source', required=True, help='name of source dataset (eg. phil-82)')
    parser.add_argument('-e', '--email', dest='email', default='', help='email for qsub completion notification')
    args = parser.parse_args()

    # handle email
    if len(args.email) > 0:
        args.email = '#$ -m e \n#$ -M '+args.email

    template = open('templates/preprocess-mzml.qsub.tmpl', 'r').read()
    template = jinja2.Template(template)
    script_text = template.render(unprocessed_mzml_file=args.mzml, sample_id=args.id, dataset=args.source, email=args.email)
    sys.stdout.write(script_text)
