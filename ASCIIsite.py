#! /usr/bin/env python3
#takes directory, converts all .adoc files to html files, copying the resulting html files to an identical directory strucuture, and copies over all non .adoc files unchanged. Optionally outputs as a tar.gz file.

import subprocess, sys, argparse, logging, tempfile, shutil, os, glob
from pathlib import Path

logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.INFO)
#logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)

def parse_arguments():
    parser=argparse.ArgumentParser(description='create a website directory structure by converting .adoc files in a directory strucutre to .html files.')
    parser.add_argument('inputDir', type=Path, help='The directory of adoc files to be copied and converted.')
    parser.add_argument('-o', '--output', type=Path, help='What to name the generated directory or tar file')
    parser.add_argument('--exclude-file', type=Path, help='A text file containing glob patterns to exclude, 1 per line.')
    parser.add_argument('--exclude', nargs='+', help='A list of glob patterns to ignore. Remember to quote them so your shell doesnt escape them!')
    parser.add_argument('-z', '--compress', action='store_true', help='whether to compress the resulting directory to a tar.gz file. can be usefull for scripting to transfer the site to a remote server.')
    args=parser.parse_args()

    #set compress flag
    if args.output != None and not args.compress:
        #detect based on whether outFile has a .tar.gz filename.
        if args.output.suffixes == ['.tar', '.gz']:
            compress=True
        else:
            compress=False
    else:
        compress=args.compress
    
    #If outfile was not set, set it.
    if args.output == None:
        baseName=args.inputDir.with_name(args.inputDir.name+'_compiled').name
        outFile=Path(os.getcwd()).joinpath(baseName)
    else:
        outFile=args.output.resolve()

    #add .tar.gz if compress is set and the outfile does not already have it.
    if compress and outFile.suffixes != ['.tar', '.gz']:
        logging.info(f'outFile was {outFile}, corrected because compress flag is set.')
        outFile=outFile.with_suffix('.tar.gz').resolve()

    if args.inputDir.resolve() == outFile.resolve():
        raise FileExistsError('output file cannot have the same path as the input file!')

    logging.debug(f'inputing from {args.inputDir.resolve()}')
    logging.info(f'outputting to {outFile.resolve()}')
    logging.debug(f'compress is {compress}')

    try:
        with open(args.exclude_file, 'r') as file:
            exclude=[glob.strip() for glob in file]

        if args.exclude != None:
            exclude.extend(args.exclude)
    except Exception as e:
        print(str(e))
        exit()

    if args.inputDir.resolve().exists():
        print(f'Inputdir {args.inputDir.resolve()} does not exist!')
        exit()

    return args.inputDir.resolve(), outFile, compress, exclude

#Doing it in a tmpDir first, as some distrubutions put temp files on a ramdisk. this should speed up the operation sigificantly.
class TmpDir:
    def __init__(self, srcDir, exclude):
        self.tmpDir=tempfile.TemporaryDirectory()
        logging.debug(f'making tmp file from {srcDir} at {self.tmpDir.name}')
        self.path=self.tmpDir.name+'/'+Path(srcDir).resolve().name
        self.ignorePatterns=['*.adoc', '.gitignore', '.git/*']
        self.ignorePatterns.extend(exclude)
        self.ignorePattern=shutil.ignore_patterns(*self.ignorePatterns)
        shutil.copytree(srcDir, self.path, ignore=self.ignorePattern, symlinks=False)

    #copy out from tmpDir (which may be in RAM, depending on distrubution) to disk
    def copy_self_to(self, destPath):
        logging.debug(f'outputting to {Path(destPath).resolve()}')
        shutil.copytree(self.path, destPath, symlinks=False)

    #copy out from tmpDir (which may be in RAM, depending on distrubution) to a compressed file on disk
    def compress_and_copy_self_to(self, destPath):
        #shutil.make_archive wants destPath to be without file extentions for some godforsaken reason.
        destPath=Path(destPath.with_name(destPath.name.split('.')[0])).resolve()
        logging.debug(f'compressing to {Path(destPath).resolve()} from {Path(self.path).parent}')
        tarFile=shutil.make_archive(destPath, 'gztar', Path(self.path).parent)

    def cleanup(self):
        self.tmpDir.cleanup()

#works on the current working directory
def find_paths_to_convert(fileNameGlob):
    return glob.glob(f'**/{fileNameGlob}', recursive=True)

#simple wrapper around the asciidoctor cli.
def convert_file(inDir, outDir, inFile):
    logging.info(f'converting {Path(inFile).resolve()}')
    logging.debug(f'converting {inFile} from directory {inDir} to directory {outDir}')
    try:
        #the destdir can be used instead of destfile in order to preserve the directory structure relative to the base dir. really useful.
        subprocess.run(['asciidoctor',
            #specifies the source directory root.
            f'--source-dir={inDir}',
            #Destination dir. It takes the file from the subtree --source-dir and puts it in the equivilant location in the subtree --destination-dir. (talking about filesystem subtrees).
            f'--destination-dir={outDir}',
            inFile],
            check=True)
    except Exception as e:
        logging.error(f'could not convert {inFile}!')
        logging.error(f'stdErr was {e.stderr}')
        logging.error(f'stdOut was {e.stdout}')

if __name__ == '__main__':
    inFile, outFile, compress, exclude=parse_arguments()
    os.chdir(inFile)
    tmpDir=TmpDir('./', exclude)
    pathsToConvert=find_paths_to_convert('*.adoc')

    for i in pathsToConvert:
        convert_file('./', tmpDir.path, i)

    if compress:
        tmpDir.compress_and_copy_self_to(outFile)
    else:
        tmpDir.copy_self_to(outFile)

    tmpDir.cleanup()
