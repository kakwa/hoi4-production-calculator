#!/bin/sh

cd `dirname $0`
cat list | while read line;
do
	if ! [ -e $line.svg ]
	then
		cp base.svg $line.svg;
	fi
	echo "current: $line"
	echo "next:    `grep -A 1 "^$line$" list | tail -n 1`"
	inkscape $line.svg;
done
