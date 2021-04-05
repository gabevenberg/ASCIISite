#! /bin/sh
#give a directory that contains a asciidoc folder and an html folder, and it will convert all asciidoc files to html files, then export the html folder to a www directory, ready to deploy as a static page.
cd "$1"

#copy the directory structure
for i in $(find ./asciidoc -type d)
do
	mkdir -p $(echo "$i" | sed s:/asciidoc/:/html/:)
done


#convert files
for i in $(find ./asciidoc -type f -name *.adoc)
do
	echo "converting $i"
	asciidoctor --destination-dir ./html/ $i
done

#package it up, ready to deploy.
cd ../ 
mkdir -p www/$1
cp -rf ./$1/html/* www/$1/
tar -c -f web.tar www
#transfer it.
