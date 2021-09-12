# ASCIIsite: an asciiDoc based static site generator.

![Licence](https://img.shields.io/badge/Licence-GPL-blue)

## What is it?
ASCIIsite is a simple, barebones static site generator. You give it a directory contaning asciidoctor documents and supporing media in the strucutre you want your site to be in, and it spits out a fully functional static site based on that input directory.

## Usage

ASCIISite takes 2 (so far) optional arguments followed by the single mandatory arument telling it what directory to convert.

the -o or --output option simply tells ASCIISite what to name the output file.

the -z or --compress flag tells ASCIISite to put the final product in a compressed tar.gz file as its output. 
This is especially useful if you are running ASCIISite on your personal computer, and will be uploading the tar.gz file to your server.

As for how to format the input directory, thats up to you. The directory structure of the input will be mirrored in the structure of the output website.
The only real rule you need to follow is that all your links to other pages in the input directory should be relative, so they dont get broken when you move the output directory around.

## Example
Say you have a nice asciidoctor directory like this:

```
test
├── dir
│   ├── collatz.py
│   └── subdir
│       └── linked.adoc
├── images
│   └── test_pattern.svg
├── include
│   └── include.adoc
└── landing_page.adoc
```

Where some pages link to others, some pages include others, and some pages have images in them.

You can run
```
ASCIISite.py -o result test
```

to get a file tree like:
```
result
├── dir
│   ├── collatz.py
│   └── subdir
│       └── linked.html
├── images
│   └── test_pattern.svg
├── include
│   └── include.html
└── landing_page.html
```

Alternatively, you can run
```
ASCIISite.py -z -o result test
```

to get a .tar.gz file containing the result directory.
