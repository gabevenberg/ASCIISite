#! /usr/bin/env python3
#takes directory, converts all .adoc files to html files, copying the resulting html files to an identical directory strucuture, and copies over all non .adoc files unchanged. Optionally outputs as a tar.gz file.

import subprocess, sys, argparse, logging, tempfile, shutil, os, re
from pathlib import Path

logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.INFO)
#logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)

def parse_arguments():
    parser=argparse.ArgumentParser(description='create a website directory structure by converting .adoc files in a directory strucutre to .html files.')
    parser.add_argument('inputDir', type=Path, help='The directory of adoc files to be copied and converted.')
    parser.add_argument('-o', '--output', type=Path, help='What to name the generated directory or tar file')
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
        outFile=args.inputDir.with_name(args.inputDir.name+'_compiled').resolve()
    else:
        outFile=args.output.resovle()

    #add .tar.gz if compress is set and the outfile does not already have it.
    if compress and outFile.suffixes != ['.tar', '.gz']:
        logging.info(f'outFile was {outFile}, corrected because compress flag is set.')
        outFile=outFile.with_suffix('.tar.gz').resolve()

    if args.inputDir.resolve() == outFile.resolve():
        raise FileExistsError('output file cannot have the same path as the input file!')

    logging.debug(f'inputing from {args.inputDir.resolve()}')
    logging.info(f'outputting to {outFile.resolve()}')
    logging.debug(f'compress is {compress}')

    return args.inputDir.resolve(), outFile, compress

#Doing it in a tmpDir first, as some distrubutions put temp files on a ramdisk. this should speed up the operation sigificantly.
class TmpDir:
    def __init__(self, srcDir):
        self.tmpDir=tempfile.TemporaryDirectory()
        logging.debug(f'making tmp file from {srcDir} at {self.tmpDir.name}')
        self.path=self.tmpDir.name+'/'+Path(srcDir).resolve().name
        self.ignorePattern=shutil.ignore_patterns('*.adoc', '.git', '.gitignore')
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

#pass an empty list to start this. It calls itself recursively
def find_paths_to_convert(inputDir, pathList):
    with os.scandir(inputDir) as it:
        for path in it:
            logging.debug(f'found {path.path}')
            if path.is_dir():
                logging.debug(f'{path.path} is directory, recursing')
                find_paths_to_convert(path, pathList)
            elif path.is_file() and re.match('^.*\.adoc$', path.name):
                logging.debug(f'adding {path.name} to pathList')
                pathList.append(Path(path.path))
    return pathList

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
    inFile, outFile, compress=parse_arguments()
    os.chdir(inFile)
    tmpDir=TmpDir('./')
    pathsToConvert=find_paths_to_convert('./', [])

    for i in pathsToConvert:
        convert_file('./', tmpDir.path, i)

    if compress:
        tmpDir.compress_and_copy_self_to(outFile)
    else:
        tmpDir.copy_self_to(outFile)

    tmpDir.cleanup()
