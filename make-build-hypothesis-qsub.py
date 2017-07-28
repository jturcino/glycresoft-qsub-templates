#!/usr/bin/env python

import jinja2
import os
import sys
import argparse

if __name__ == '__main__':

    # arguments
    parser = argparse.ArgumentParser(description='Make build-hypthesis qsub script for glycan-combinatorial or glycan-text. All filepaths should be relative to the directory from which the qsub script will be submitted. The output database will be placed in the submission directory.')
    parser.add_argument('-d', '--db', dest='db', required=True, help='name of output database file')
    parser.add_argument('-s', '--source', dest='source', required=True, help='name of source dataset (eg. phil-82)')
    parser.add_argument('-m', '--mzid', dest='mzid', help='path to mzIdentML file; creates a mzid hypothesis')
    parser.add_argument('-f', '--fa', dest='fa', help='path to .fa file; creates a fa hypothesis')
    parser.add_argument('-r', '--rules', dest='rules', help='path to combinatorial rules file; creates combinatorial qsub')
    parser.add_argument('-g', '--glycans', dest='glycans', help='path to glycans file; creates text qsub')
    parser.add_argument('-e', '--email', dest='email', default='', help='email for qsub completion notification')
    args = parser.parse_args()

    # if neither or both -m and -f flags are given, exit
    if (args.mzid is None and args.fa is None) or (args.mzid is not None and args.fa is not None):
        print 'Please give either -m or -f'
        exit(0)

    # if neither or both -r and -g flags are given, exit
    elif (args.rules is None and args.glycans is None) or (args.rules is not None and args.glycans is not None):
        print 'Please give either -r or -g'
        exit(0)

    # get template and kwargs
    template_file = None
    kwargs = {'db': args.db, 'source': args.source}
    if args.mzid is not None:
        kwargs['mzid_file'] = args.mzid
        if args.rules is not None:
            kwargs['combo_rules'] = args.rules
            template_file = 'build-hypothesis-combinatorial-mzid.qsub.tmpl'
        else: # args.glycans is not None
            kwargs['nglycans'] = args.glycans
            template_file = 'build-hypothesis-text-mzid.qsub.tmpl'

    else: # args.fa is not None
        kwargs['fa_file'] = args.fa
        if args.rules is not None:
            kwargs['combo_rules'] = args.rules
            template_file = 'build-hypothesis-combinatorial-fa.qsub.tmpl'
        else: # args.glycans is not None
            kwargs['nglycans'] = args.glycans
            template_file = 'build-hypothesis-text-fa.qsub.tmpl'

    # handle email
    if len(args.email) > 0:
        args.email = '#$ -m e \n#$ -M '+args.email
    kwargs['email'] = args.email

    # open template, insert values, and print contents
    assert template_file is not None, 'Template filename not assigned'
    assert len(kwargs.keys()) == 5, 'kwargs has '+str(len(kwargs.keys()))+' keys != 4'

    template = open(template_file, 'r').read()
    template = jinja2.Template(template)
    script_text = template.render(**kwargs)

    sys.stdout.write(script_text)
