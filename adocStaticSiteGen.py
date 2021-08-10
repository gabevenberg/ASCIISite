#! /usr/bin/env python3
#takes directory, converts all .adoc files to html files, copying the resulting html files to an identical directory strucuture, and copies over all non .adoc files unchanged. Optionally outputs as a tar.gz file.

import subprocess, sys, argparse, logging, tempfile, shutil
from pathlib import Path

#logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.INFO)
logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)

def parse_arguments():
    parser = argparse.ArgumentParser(description='create a website directory structure by converting .adoc files in a directory strucutre to .html files.')
    parser.add_argument('inputDir', type=Path, help='The directory of adoc files to be copied and converted.')
    parser.add_argument('-o', '--output', type=Path, help='What to name the generated directory or tar file')
    parser.add_argument('-z', '--compress', action='store_true', help='whether to compress the resulting directory to a tar.gz file. can be usefull for scripting to transfer the site to a remote server.')
    args=parser.parse_args()

    if args.output != None and not args.compress:
        #detect based on whether outFile has a .tar.gz filename.
        if args.output.suffixes == ['.tar', '.gz']:
            compress = True
        else:
            compress = False
    else:
        compress = args.compress
    
    if args.output == None:
        outFile = args.inputDir.with_name(args.inputDir.name+'_compiled')
    else:
        outFile=args.output

    if compress and outFile.suffixes != ['.tar', '.gz']:
        logging.debug(f'outFile was {outFile}, corrected because compress flag is set.')
        outFile = outFile.with_suffix('.tar.gz')

    logging.debug(f'inputing from {args.inputDir.resolve()}')
    logging.info(f'outputting to {outFile.resolve()}')
    logging.debug(f'compress is {compress}')

    if args.inputDir.resolve() == outFile.resolve():
        raise FileExistsError('output file cannot have the same path as the input file!')

    return args.inputDir, outFile, compress

class TmpDir:
    def __init__(self, srcDir):
        logging.debug('making tmp file')
        self.tmpDir = tempfile.TemporaryDirectory()
        self.path = self.tmpDir.name+'/data/'
        self.ignorePattern = shutil.ignore_patterns('*.adoc', '.git', '.gitignore')
        shutil.copytree(srcDir, self.path, ignore = self.ignorePattern, symlinks=False)

    def copy_self_to(self, destDir):
        shutil.copytree(self.path, destDir, symlinks=False)

    def compress_and_copy_self_to(self, destPath):
        #shutil.make_archive wants destPath to be without file extentions for some godforsaken reason.
        destPath = Path(destPath.with_name(destPath.name.split('.')[0])).resolve()
        logging.debug(f'outputting to {destPath}')
        tarFile = shutil.make_archive(destPath, 'gztar', self.path)

    def cleanup(self):
        self.tmpDir.cleanup()

inputDir, outFile, compress = parse_arguments()
tmpdir = TmpDir(inputDir)
print(tmpdir.path)
breakpoint()
tmpdir.compress_and_copy_self_to(outFile)
tmpdir.cleanup()
