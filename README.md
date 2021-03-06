# consensus-highlighter

Latest version is `2.3.a` (2022-04-26 edition).

## Description

This program annotates low-coverage regions of sequences in fasta format.

### Input

1. The target sequence(s) in fasta format.
2. The mapping in **sorted** BAM file.
3. Coverage threshold(s) for searching low-coverage regions.

### Output

- A GenBank file with annotated low-coverage regions.

## Dependencies

- [Python](https://www.python.org/downloads/) 3.6 or later.
- [Biopython](https://biopython.org/) package.
- [samtools](https://github.com/samtools/samtools) 1.13 or later is recommended. Versions from 1.11 to 1.12 are acceptable, but might calculate coverage inaccurately.

You can install Biopython wi following command:
```
pip3 install biopython
```

I recommend to install samtools by downloading latest release from [samtools page](https://github.com/samtools/samtools) on github. Then follow instrunctions in downloaded INSTALL file.

## Usage

Basic usage is:
```
./consensus-highlighter.py -f <TARGET_FASTA> -b <MAPPING_BAM>
```

You can specify custom coverage theshold(s) by passing comma-separated list of thresholds with option `-c`. For example, following command will annotate all regions with coverage below 25 and all regions below 55 (and also with zero coverage):

```
./consensus-highlighter.py -f my_sequence.fasta -b my_mapping.sorted.bam -c 25,55
```

### Options

```
-f or --target-fasta: *
    File of target sequence(s) in fasta format.
-b or --bam: *
    Sorted BAM file which contains mapping on target sequence(s).
-o or --outfile:
    Output file.
    Deault value: 'highlighted_sequence.gbk'.
-c or --coverage-thresholds:
    Comma-separated list of coverage threshold(s).
    Default: 10.
-n or --no-zero-output:
    Suppress annotation of zero-coverage regions.
    Disabled by default.
--circular:
    Target sequence in curcular. Affects only corresponding GenBank field.
    Disabled by default.
--organism:
    Organism name. Affects only corresponding GenBank field.
    If it contains spaces, surround it with quotes (see Example 4).
    Empty by default.
```
\* - mandatory option


## Examples

### Example 1

Annotate low-coverage regions in sequence `my_sequence.fasta` with default parameters according to mapping from file `my_mapping.sorted.bam`:

```
./consensus-highlighter.py -f my_sequence.fasta -b my_mapping.sorted.bam
```

### Example 2

Annotate low-coverage regions in sequence `my_sequence.fasta` according to mapping from file `my_mapping.sorted.bam`. Annotate regions with coverage below 25, fragments with coverages below 50 and regions with zero coverages:

```
./consensus-highlighter.py -f my_sequence.fasta -b my_mapping.sorted.bam -c 25,50
```

### Example 3

Annotate low-coverage regions in sequence `my_sequence.fasta` according to mapping from file `my_mapping.sorted.bam`. Annotate regions with coverage below 25, fragments with coverages below 50. Suppress annotation of zerocoverage regions:

```
./consensus-highlighter.py -f my_sequence.fasta -b my_mapping.sorted.bam -c 25,50 -n
```

### Example 4

Annotate low-coverage regions in sequence `my_sequence.fasta` with default parameters according to mapping from file `my_mapping.sorted.bam`. Specify the name of the organism for output file. The sequence is circular:

```
./consensus-highlighter.py -f my_sequence.fasta -b my_mapping.sorted.bam \
    --circular --organism "Serratia marcescens"
```
