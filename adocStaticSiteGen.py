#! /usr/bin/env python3
#takes directory, converts all .adoc files to html files, copying the resulting html files to an identical directory strucuture, and copies over all non .adoc files unchanged. Optionally outputs as a tar.gz file.

import subprocess, sys, argparse, logging
from pathlib import Path

logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.INFO)
#logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputDir', type=Path, help='The directory of adoc files to be copied and converted.')
    parser.add_argument('-o', '--output', type=Path, help='What to name the generated directory or tar file')
    parser.add_argument('-z', '--compress', action='store_true')
    args=parser.parse_args()

    if args.output != None and args.compress == False:
        #detect based on whether outFile has a .tar.gz filename.
        if args.output.suffixes == ['.tar', '.gz']:
            compress = True
        else:
            compress = False
    else:
        compress = args.compress
    
    if args.output == None:
        outfile = Path(args.inputDir.parent).joinpath(args.inputdir.stem)
    else:
        outfile=args.output

    logging.info(f'outputting to {outFile}')

    return args.inputDir, outfile, compress
