# geneCutterParser
Parses results HIV LANL Database Gene Cutter tool to get coordinates for potential alignments

## Requirements:
- Check requirements.txt for installation dependencies
- Python 3+
- Requires BioPython=1.79

## Steps:
1. Procure a fasta file of HIV sequences. Each fasta record should have an unique name. Fasta file should not be pre-aligned.
2. Submit fasta file to the (HIV LANL Gene Cutter tool)[https://www.hiv.lanl.gov/content/sequence/GENE_CUTTER/cutter.html] for HIV with the following settings:
  - Uncheck "Input sequences are pre-aligned"
  - Check "Do not translate"
  - Keep all other default settings
3. After Gene Cutter is finished, download the compressed results.
4. Unzip/decompress the results file.
5. Run geneCutterParser (see below for arguments)

## Example run
```{bash}
python parser.py --subjectSequences my.fasta --runID="A01" --geneCutterResults geneCutterResultsDirectory
```


## Arguments
> `--subjectSequences`

(required) Fasta file. HIV sequences used for input into Gene Cutter. Fasta record names must match original input.

> `--runID`

(required) Run ID used to name output file.

> `--geneCutterResults`

(required) Directory containing Gene Cutter Results (should be multiple .na.fasta files present).

> `--outputDir`

(optional) Output folder. [defaults to current directory]