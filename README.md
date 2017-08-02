# glycresoft-qsub-templates

A way to generate qsub scripts for running GlycReSoft on the Boston University Shared Computing Cluster (SCC)

## Getting Started
To use this repo, clone it into a directory of your choosing and add the `glycresoft-cli` to your path.
```
# clone this repo
cd [destination of this repo]
git init
git clone https://github.com/jturcino/glycresoft-qsub-templates.git

# add path to glycresoft-cli to $PATH
echo "export PATH=$PATH:[absolute path to directory with glycresoft-cli]" >> ~/.bashrc
```

## Generating qsubs
To generate a set of qsubs, only five items are needed:
1. absolute path to the directory from which you plan to submit the qsub scripts
2. path to an mzIdentML file or fasta file
3. path to a combinatorial rules file or nglycan file
4. path to at least one unprocessed or preprocessed mzML file (can have multiple of one or both types)
5. project name

The paths for items 2-4 should be either absolute paths or paths relative to the project directory (item 1).

### Standard submission
A typical submission would resemble the following. Please note the `-m` flag and mzIdentML filepath may be substituted with the `-f` flag and fasta filepath. Similarly, the `-r` flag and combinatorial rules file may be substituted with the `-g` flag and nglycans filepath.
```
./generate-glycresoft-qsubs.sh -d /some/absolute/path -m /some/file.mzid -r /using/some/rules.txt -y /here/is/unprocessed.mzML -z /here/is/processed.mzML -p project-name
```

You may notice there are now three subdirectories in your project directory. These are created by `generate-glycresoft-qsubs.sh` to avoid cluttering the project directory. The `preprocess` subdirectory will hold all the preprocessed mzML files produced by `preprocess-mzml` qsubs. The `search` subdirectory will hold all the database files created by the `search-glycopeptide` qsubs. Lastly, the 
`glycopeptide_csvs` subdirectory will hold the CSV files that are the final product of the GlycReSoft pipeline.

### Additional options
All currently available options can be viewed at any time with the `-h` flag.
```
./generate-glycresoft-qsubs.sh -h
```
Below are the optional arguments currently available:
* `-e` sends an email to the provided address upon completion of each qsub script
* `-s` specifies the time to begin processing information in the unprocessed mzML files (`-y`); defaults to 12.0
* `-t` specifies the time to stop processing information in the unprocessed mzML files; defaults to 50.0

## qsub submission
Once generated, the qsubs must be submitted in the following order:
1. All `preprocess-mzml` qsubs (if present)
2. `build-hypothesis` qsub
3. All `search-glycopeptide` qsubs
4. All `glycopeptide-identification` qsubs

The qsubs should be submitted to the scheduler from the commandline. The submission command follows the format `qusb -P SCC_PROJECT -pe omp NUM_PROCESSORS QSUB_FILE`. `NUM_PROCESSORS` should aways be **4** except for proprocessing qsubs, where **6** should be used. An example is below.
```
# SCC_PROJECT is glyco-ms

# submitting preprocessing qsub
qsub -P glyco-ms -pe omp 6 preprocess-mzml-project-name-unprocessed.qsub

# submitting a hypothesis qsub
qsub -P glyco-ms -pe omp 4 build-hypothesis-combinatorial-project-name.qsub
```

### Submitting multiple qsubs
For a given project, you may be submitting multiple `preprocess-mzml`, `search-glycopeptide`, and/or `glycopeptide-identification` qsubs at once. If so, a bash submission for loop may be of use to you. Examples are below.
```
# in project dir
# submit preprocess-mzml qsubs
for i in $(ls preprocess-mzml*.qsub); do
    qsub -P glyco-ms -pe omp 6 $i
done

# submit search-glycopeptide qsubs
for i in $(ls search-glycopeptide*.qsub); do
    qsub -P glyco-ms -pe omp 4 $i
done

# submit glycopeptide-identification qsubs
for i in $(ls glycopeptide-identification*.qsub); do
    qsub -P glyco-ms -pe omp 4 $i
done
```

