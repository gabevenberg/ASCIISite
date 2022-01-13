rm -r result
../ASCIIsite.py --verbose --output result --exclude-file globignore test
#find the sha1sum of the output
cd result
result=$(find . -type f -print0 | xargs -0 -P0 -n1 md5sum | sort -k 2 | md5sum)
cd ../control
control=$(find . -type f -print0 | xargs -0 -P0 -n1 md5sum | sort -k 2 | md5sum)
cd ../
tree result
echo result sum is $result
echo control sum is $control
if [ "$result" = "$control" ]; then
	echo test passed!
else
	echo test did not pass!!!!!
fi
rm -r result_css
../ASCIIsite.py --verbose --output result_css --exclude-file globignore --stylesheet test.css test
cd result_css
result_css=$(find . -type f -print0 | xargs -0 -P0 -n1 md5sum | sort -k 2 | md5sum)
cd ../control_css
control_css=$(find . -type f -print0 | xargs -0 -P0 -n1 md5sum | sort -k 2 | md5sum)
cd ../
tree result_css
echo result_css sum is $result_css
echo control_css sum is $control_css
if [ "$result_css" = "$control_css" ]; then
	echo test passed!
else
	echo test did not pass!!!!!
fi
