#!/usr/bin/env bash

HELP="
Creates qsub scripts for running glycresoft and saves them in the submission
directory provided with the -d flag. Please note either a mzIdentML hypothesis
or a FASTA hypothesis can be created; use the appropriate flag (-m or -f). 
Similarly, either a combinatorial hypothesis or a text hypothesis; use the
appropriate flag (-r or -g). All files created via the qsub scripts will be 
stored in the submission directory. 

IMPORTANT NOTES: 
* all filepaths provided should be relative to the project directory (-d)
* the project directory (-d) should be an absolute path
* providing an mzIdentML file (-m) produces a mzid hypotheis; a fasta file 
  (-f) produces a fasta hypothesis
* providing a combinatorial rules file (-r) produces a combinatorial hypothesis; 
  a glycan file (-g) produces a text hypothesis

Usage: ./generate-glycresoft-qsubs.sh [OPTIONS]

Options:
  -h, --HELP                            Prints this message
  -p, --project PROJECT_NAME            Name of glycresoft project
  -d, --dir DIRECTORY                   Path to project directory from current
  -f, --fa FASTA                        Path to fasta file
  -m, --mzid MZID                       Path to mzIdentML file
  -r, --rules COMBINATORIAL_RULES       Path to combinatorial rule file
  -g, --glycans GLYCANS                 Path to nglycan file
  -y, --unprocessed-mzml MZML           Path to unprocessed mzML file
  -z, --processed-mzml MZML             Path to preprocessed mzML file
  -e, --email EMAIL                     (Optional) Email address for qsub notifications
  -s, --start-time TIME			(Optional) Time to begin processing unprocessed 
         					   mzML files (default 12.0)
  -t, --end-time TIME			(Optional) Time to end processing unprocessed 
						   mzML files (default 50.0)
"

while [[ $# -gt 1 ]]; do
    key="$1"
    case $key in
        -p|--project) shift;
            project_name="$1"
            shift ;;
        -d|--dir) shift;
            submission_dir="$1"
            shift ;;
        -f|--fa) shift;
            fa="$1"
            shift ;;
        -m|--mzid) shift;
            mzid="$1"
            shift ;;
        -r|--rules) shift;
            combo_rules="$1"
            shift ;;
        -g|--glycans) shift;
            glycans="$1"
            shift ;;
        -y|--unprocessed-mzml) shift;
            pre_mzmls="$pre_mzmls $1"
            shift ;;
        -z|--processed-mzml) shift;
            mzmls="$mzmls $1"
            shift ;;
        -e|--email) shift;
            email="-e $1"
            shift ;;
	-s|--start-time) shift;
	    begin="-st $1"
	    shift ;;
	-t|--end-time) shift;
	    end="-et $1"
	    shift ;;
        *) echo "$HELP"
            exit 0
    esac
done

# check for help request
if [ "$1" == "-h" ]; then
    echo "$HELP"
    exit 0
fi

# check for mzid/fa and set mzid_fa
mzid_fa=""
if [ -z "$mzid" ] && [ -z "$fa" ]; then
    echo "Either mzid or fa filepath must be provided"
    exit 1
elif [ ! -z "$mzid" ] && [ ! -z "$fa" ]; then
    echo "Either provide an mzid filepath or fa filepath; do not provide both"
    exit 1
elif [ ! -z "$mzid" ]; then
    mzid_fa="-m $mzid"
else
    mzid_fa="-f $fa"
fi

# check for combinatorial/nglycans
if [ -z "$combo_rules" ] && [ -z "$glycans" ]; then
    echo "Either a combinatorial rules file or nglycan file must be provided"
    exit 1
elif [ ! -z "$combo_rules" ] && [ ! -z "$glycans" ]; then
    echo "Either provide a combinatorial rules file nglycan file; do not provide both"
    exit 1
fi

# check for combo rules, project name, submission directory, and
# at least one mzML file
if [ -z "$project_name" ]; then
    echo "Please project a glycresoft project name"
    exit 1
elif [ -z "$submission_dir" ]; then
    echo "Please provide a qsub submission directory"
    exit 1
elif [ -z "$pre_mzmls$mzmls" ]; then
    echo "Please provide at least one preprocessed or unprocessed mzML file"
    exit 1
fi

# make outdir
echo "Making subdirectories under $submission_dir..."
mkdir -p "$submission_dir/preprocess"
mkdir -p "$submission_dir/search"
mkdir -p "$submission_dir/glycopeptide_csvs"

# preprocess mzml files
echo "Making preprocess mzML for"
for mzml in $pre_mzmls; do
    id="$(basename $mzml)"
    id="${id%%.*}"
    echo "    $id..."
    ./scripts/make-preprocess-mzml-qsub.py -m $mzml -i $id -s $project_name $email $begin $end >> $submission_dir/preprocess-mzml-$project_name-$id.qsub
    out="preprocess/$id.preprocessed.mzML"
    mzmls="$mzmls $out"
done

# build combinatorial hypothesis
#echo "Making combinatorial hypothesis..."
#combo_hypothesis="$project_name-hypothesis.db"
#./scripts/make-build-hypothesis-qsub.py $mzid_fa -r $combo_rules -s $project_name -d $combo_hypothesis $email >> $submission_dir/build-hypothesis-combinatorial-$project_name.qsub

# build hypothesis (combinatorial or text)
hypothesis="$project_name-hypothesis.db"
if [ ! -z "$glycans" ]; then
    echo "Making text hypothesis..."
    ./scripts/make-build-hypothesis-qsub.py $mzid_fa $email -g $glycans -s $project_name -d $hypothesis >> $submission_dir/build-hypothesis-text-$project_name.qsub
else
    echo "Making combinatorial hypothesis..."
    ./scripts/make-build-hypothesis-qsub.py $mzid_fa $email -r $combo_rules -s $project_name -d $hypothesis >> $submission_dir/build-hypothesis-combinatorial-$project_name.qsub
fi

# search for glycopeptides
echo "Searching for glycopeptides for"
dbs=""
for mzml in $mzmls; do
    id="$(basename $mzml)"
    id="${id%%.*}"
    echo "    $id..."
    db="$id.db"
    ./scripts/make-search-glycopeptide-qsub.py -m $mzml -d $hypothesis -i $id -s $project_name -o $db $email >> $submission_dir/search-glycopeptide-$project_name-$id.qsub
    dbs="$dbs search/$db"
done

# identify glycopeptides
echo "Identifying glycopeptides for"
csv_args=""
for db in $dbs; do
    id="$(basename $db)"
    id="${id%%.*}"
    echo "    $id..."
    csv="${id}_glycopeptides.csv"
    ./scripts/make-glycopeptide-identification-qsub.py -d $db -c $csv -i $id -s $project_name $email >> $submission_dir/glycopeptide-identification-$project_name-$id.qsub
    csv_args="$csv_args -c glycopeptide_csvs/$csv"
done

## EXIT HERE IF ROUND 2 PROCESSING NOT SPECIFIED
#if [ -z "$glycans" ]; then
#    exit 0
#else
#    echo 'Making qsubs for second round of processing...'
#fi
#
## run pandas
#echo "Consolidating unique glycans..."
#./scripts/make-consolidate-glycans-qsub.py $csv_args -s $project_name -o $glycans $email >> $submission_dir/consolidate-glycans-$project_name.qsub
#
## build text hypothesis
#echo "Making restricted text hypothesis..."
#text_hypothesis="$project_name-hypothesis-restricted.db"
#./scripts/make-build-hypothesis-qsub.py $mzid_fa -g $glycans -s $project_name-restricted -d $text_hypothesis $email >> $submission_dir/build-hypothesis-text-$project_name-restricted.qsub
#
## search glycopeptides (restricted)
#echo "Searching for glycopeptides for"
#restricted_dbs=""
#for mzml in $mzmls; do
#    id="$(basename $mzml)"
#    id="${id%%.*}-restricted"
#    echo "    $id..."
#    db="$id.db"
#    ./scripts/make-search-glycopeptide-qsub.py -m $mzml -d $text_hypothesis -o $db -i $id -s $project_name-restricted $email >> $submission_dir/search-glycopeptide-$project_name-restricted-$id.qsub
#    restricted_dbs="$restricted_dbs search/$db"
#done

# generate restriced csvs
#echo "Identifying restricted sets of glycopeptides for"
#for db in $restricted_dbs; do
#    id="$(basename $db)"
#    id="${id%%.*}"
#    echo "    $id..."
#    csv="${id}_glycopeptides.csv"
#    ./scripts/make-glycopeptide-identification-qsub.py -d $db -c $csv -i $id -s $project_name-restricted $email >> $submission_dir/glycopeptide-identification-$project_name-restricted-$id.qsub
#done
