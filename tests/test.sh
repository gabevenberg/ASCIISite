rm -r result
../ASCIIsite.py --verbose --output result --exclude-file globignore test
#find the sha1sum of the output
cd result
result=$(find . -type f -print0 | xargs -0 -P0 -n1 md5sum | sort -k 2 | md5sum)
cd ../control
control=$(find . -type f -print0 | xargs -0 -P0 -n1 md5sum | sort -k 2 | md5sum)
cd ../
echo result sum is $result
echo control sum is $control
if [ "$result" = "$control" ]; then
	echo test passed!
else
	echo test did not pass!!!!!
fi
