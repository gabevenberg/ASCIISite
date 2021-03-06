# ASCIIsite: an asciiDoc based static site generator.

![Licence](https://img.shields.io/badge/Licence-GPL-blue)

## What is it?
ASCIIsite is a simple, bare bones static site generator. You give it a directory containing asciidoctor documents and supporting media in the structure you want your site to be in, and it spits out a fully functional static site based on that input directory.

## Usage

ASCIISite several optional arguments followed by a single mandatory argument telling it what directory to convert.

the -o or --output option simply tells ASCIISite what to name the output file.

the -z or --compress flag tells ASCIISite to put the final product in a compressed tar.gz file as its output. 
This is especially useful if you are running ASCIISite on your personal computer, and will be uploading the tar.gz file to your server.

The --sylesheet options allows you to set a custom stylesheet to use instead of the default ASCIIDoctor stylesheet.

The --exclude flag allows you to specify a list of glob patterns. Any file matching these glob patterns will not be copied to the output.

The --exclude-file flag allows you to specify a file containing one glob to exclude per line. Other than inputting from a file, works exactly the same as --exclude. Note that it cannot parse the full spec of .gitignore files, only traditional globs.

Exclusions are helpful for any files that are needed for the compilation of the asciidoc files, but do not need to be in the final site.
The main use case I am aware of is files that are put into an asciidoc document via an include statement.

As for how to format the input directory, thats up to you. The directory structure of the input will be mirrored in the structure of the output website.
The only real rule you need to follow is that all your links to other pages in the input directory should be relative, so they dont get broken when you move the output directory around.

## Example
Say you have a nice asciidoctor directory like this:

```
test
├── dir
│   └── subdir
│       └── linked.adoc
├── images
│   └── test_pattern.svg
├── include
│   └── include.txt
└── landing_page.adoc
```

Where some pages link to others, some pages include others, and some pages have images in them.

You can run
```
ASCIISite.py -o output test
```

to get a file tree like:
```
output
├── css
│   └── asciidoctor.css
├── dir
│   └── subdir
│       └── linked.html
├── include
│   └── include.txt
├── images
│   └── test_pattern.svg
└── landing_page.html
```

If, say, the include directory is a directory needed for the asciidoc compilation,
but not needed for the final website, you can use the --exclude option to specify a list of glob patterns to exclude. For example, 
````
ASCIIsite.py --exclude 'include*' -o output test
```

will get you an output like:
```
output
├── css
│   └── asciidoctor.css
├── dir
│   └── subdir
│       └── linked.html
├── images
│   └── test_pattern.svg
└── landing_page.html
```

and, to use your custom stylesheet named `+myTheme.css+`, you can use:

```
ASCIIsite.py --stylesheet myTheme.css -o output test
```

```
output
├── css
│   └── myTheme.css
├── dir
│   └── subdir
│       └── linked.html
├── include
│   └── include.txt
├── images
│   └── test_pattern.svg
└── landing_page.html
```

Alternatively, you can run

```
ASCIISite.py -z -o output test
```

to get a .tar.gz file containing the output directory.
