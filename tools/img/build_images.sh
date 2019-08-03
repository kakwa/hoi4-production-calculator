#!/bin/sh


IMG_PATH="$HOME/.steam/steam/steamapps/common/Hearts of Iron IV/gfx/interface/technologies"

sed 's/ *//g' index_equipement.txt | while read line
do
	echo "$line"
	year=`echo $line | cut -d ':' -f 1`
	eq_type=`echo $line | cut -d ':' -f 2`
	eq_img=`echo $line | cut -d ':' -f 3`
	eq_img_addon=`echo $line | cut -d ':' -f 4`
	path="../../img/equipement/$year/"
	mkdir -p $path
	img_source="`find \"$IMG_PATH\" -name $eq_img`"
	convert "$img_source" $path/$eq_type.png
	if ! [ -z "$eq_img_addon" ]
	then
		addon_source="`find \"$IMG_PATH\" -name $eq_img_addon`"
		convert "$img_source" "$addon_source" -gravity NorthEast -compose over -composite $path/$eq_type.png
	fi
done

