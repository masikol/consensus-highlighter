# -*- encoding: utf-8 -*-
# Version 1.0.a

import os
import re
import sys
import getopt
from typing import List, Sequence, Iterable

from src.print_help import print_help
from src.platform import platf_depend_exit
from src.coverage_threshold import CoverageTheshold


class HighlighterParams:
    # Class-container for storing run parameters

    def __init__(
        self,
        target_fasta_fpath: str,
        bam_fpath: str,
        outdir_path: str,
        coverage_thresholds: Sequence[int],
        suppress_zero_cov_output: bool,
        topology: str,
        organism: str,
        outfile_prefix: str
    ) -> None:

        self.target_fasta_fpath: str = target_fasta_fpath
        self.bam_fpath: str = bam_fpath
        self.outdir_path: str = outdir_path

        self.suppress_zero_cov_output = suppress_zero_cov_output

        self.set_coverage_thresholds(coverage_thresholds)

        self.topology = topology
        self.organism: str = organism

        self.outfile_prefix = outfile_prefix

    # end def __init__


    def set_coverage_thresholds(self, coverage_thresholds: Sequence[int]) -> None:

        self.coverage_thresholds: Sequence[CoverageTheshold]

        if self.suppress_zero_cov_output:
            coverage_thresholds = tuple(filter(lambda x: x != 0, coverage_thresholds))
        # end if

        self.coverage_thresholds = tuple(
            (CoverageTheshold(cov) for cov in coverage_thresholds)
        )
    # end def set_coverage_thresholds


    def __repr__(self) -> str:
        return f"""HighlighterParams(
  target_fasta_fpath: `{self.target_fasta_fpath}`
  bam_fpath: `{self.bam_fpath}`
  outdir_path: `{self.outdir_path}`
  coverage_thresholds: {self.coverage_thresholds}
  suppress_zero_cov_output: {self.suppress_zero_cov_output}
  topology: {self.topology}
  organism: `{self.organism}`
  outfile_prefix: `{self.outfile_prefix}`
)"""
    # end def __repr__

# end class HighlighterParams


def parse_arguments(version: str, last_update_date: str) -> HighlighterParams:
    # Function parses command line arguments and produces
    #   container with program parameters in it.

    # Print help message and exit if required
    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        print_help(version, last_update_date)
        platf_depend_exit()
    # end if

    # Print version and exit if required
    if '-v' in sys.argv[1:] or '--version' in sys.argv[1:]:
        print(version)
        platf_depend_exit()
    # end if

    # Parse arguments with getopt
    opts: List[List[str]]
    args: List[str]
    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:],
            'hvf:b:o:c:n',
            [
                'help',
                'version',
                'target-fasta=',
                'bam=',
                'outdir=',
                'coverage-thresholds=',
                'no-zero-output',
                'circular',
                'organism=',
                'prefix='
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        platf_depend_exit(2)
    # end try

    # Check positional arguments: their existance is an error signal
    if len(args) != 0:
        print('Error: consensus-highlighter.py does not take any positional arguments.')
        print('You passed following positional argument(s):')
        arg: str
        for arg in args:
            print(f'  `{arg}`')
        # end for
        platf_depend_exit(2)
    # end if

    # Parse options
    params: HighlighterParams = _parse_options(opts)

    # Check mandatory options
    if params.target_fasta_fpath is None:
        print('Error: option `-f` (`--target-fasta`) is mandatory.')
        platf_depend_exit(2)
    # end if

    if params.bam_fpath is None:
        print('Error: option `-b` (`--bam`) is mandatory.')
        platf_depend_exit(2)
    # end if

    return params
# end def parse_arguments


def _parse_options(opts: List[List[str]]) -> HighlighterParams:
    # Function parses program options

    # Initialize run parameters with default values
    params: HighlighterParams = HighlighterParams(
        target_fasta_fpath=None,
        bam_fpath=None,
        outdir_path=os.path.join(os.getcwd(), 'consensus-highlighter-output'),
        coverage_thresholds=(10,),
        suppress_zero_cov_output=False,
        topology='linear',
        organism='.',
        outfile_prefix=''
    )

    # Parse command line options
    opt: str
    arg: str
    for opt, arg in opts:

        # Target fasta file
        if opt in ('-f', '--target-fasta'):

            if not os.path.isfile(arg):
                print(f'\aError: file {arg}` does not exist.')
                platf_depend_exit(2)
            # end if

            if not _is_fasta(arg):
                print('\aError: only plain fasta or gzipped fasta are supported.')
                print(f'Erroneous file: `{arg}`.')
                print('Allowed extentions: `.fasta`, `.fa`, `.fasta.gz`, `.fa.gz`.')
                platf_depend_exit(2)
            # end if

            params.target_fasta_fpath = arg

        # BAM file
        elif opt in ('-b', '--bam'):

            if not os.path.isfile(arg):
                print(f'\aError: file {arg}` does not exist.')
                platf_depend_exit(2)
            # end if

            if not _is_bam(arg):
                print(f'\aError: file `{arg}` does not seem like a BAM file.')
                print('The program only accepts BAM files having `.bam` extentions')
                platf_depend_exit(2)
            # end if

            params.bam_fpath = arg

        # Output directory
        elif opt in ('-o', '--outdir'):
            params.outdir_path = os.path.abspath(arg)

        # List of coverage thesholds
        elif opt in ('-c', '--coverage-thresholds'):

            cov_strings: Sequence[str] = arg.split(',')

            if any(map(_coverage_not_parsable, cov_strings)):

                invalid_strings: Iterable[str] = filter(_coverage_not_parsable, cov_strings)

                print(f'\aError: invalid coverage thresholds in `{arg}`:')
                for s in invalid_strings:
                    print(f'  `{s}`')
                # end for
                print('Coverage thesholds must be positive integer numbers.')
                platf_depend_exit(2)
            # end if

            # Now cast coverages to int
            coverage_thresholds: Sequence[int] = tuple(
                (int(cov_str) for cov_str in cov_strings)
            )

            params.set_coverage_thresholds(coverage_thresholds)

        # Repress zero output
        elif opt in ('-n', '--no-zero-output'):
            params.suppress_zero_cov_output = True

        # Molecule topology for annotation
        elif opt == '--circular':
            params.topology = 'circular'

        # Organism name for annotation
        elif opt == '--organism':
            params.organism = arg

        # Prefix for output files
        elif opt == '--prefix':
            params.outfile_prefix = arg
        # end if
    # end for

    # Add zero coverage threshold, if no suppression is specified
    if not params.suppress_zero_cov_output:
        _add_zero_theshold(params)
    # end if

    return params
# end def _parse_options


def _is_fasta(fpath: str) -> bool:
    fasta_pattern: str = r'.+\.f(ast)?a(\.gz)?'
    return not re.match(fasta_pattern, fpath) is None
# end def _is_fasta


def _is_bam(fpath: str) -> bool:
    bam_pattern: str = r'.+\.bam'
    return not re.match(bam_pattern, fpath) is None
# end def _is_bam


def _add_zero_theshold(params: HighlighterParams) -> None:
    # Function adds zero threshold to lost of coverage thresholds
    # :param params: program parameters;

    curr_coverage_thresholds: Sequence[int] = tuple(
        map(
            lambda x: x.get_coverage(),
            params.coverage_thresholds
        )
    )

    coverage_thresholds_with_zero: Sequence[int] = (0,) + curr_coverage_thresholds

    params.set_coverage_thresholds(coverage_thresholds_with_zero)
# end def _add_zero_theshold


def _coverage_not_parsable(string: str) -> bool:
    # Function checks validity of coverage threshold strign representation
    # :param string: string to validate;

    cov_is_not_parsable: bool = True

    try:
        cov: int = int(string)
        if cov < 1:
            raise ValueError
        # end if
    except ValueError:
        cov_is_not_parsable = True
    else:
        cov_is_not_parsable = False
    # end try

    return cov_is_not_parsable
# end def _coverage_not_parsable
