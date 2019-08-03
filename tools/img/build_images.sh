#!/bin/sh


IMG_PATH="$HOME/.steam/steam/steamapps/common/Hearts of Iron IV/gfx/interface/technologies/"

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



IMG_PATH="$HOME/.steam/steam/steamapps/common/Hearts of Iron IV/gfx/interface/counters/divisions_large/"

sed 's/ *//g' index_unit.txt | while read line
do
	echo "$line"
	family=`echo $line | cut -d ':' -f 1`
	unit=`echo $line | cut -d ':' -f 2`
	unit_img=`echo $line | cut -d ':' -f 3`
	path="../../img/unit/$family/"
	mkdir -p $path
	img_source="`find \"$IMG_PATH\" -name $unit_img`"
	convert "$img_source" $path/$unit_img.png
done

echo "factory.png"
IMG_PATH="$HOME/.steam/steam/steamapps/common/Hearts of Iron IV/gfx/interface/factory_icon.dds"
path="../../img/misc/"
mkdir -p $path
convert "$IMG_PATH" "$path/factory.png"
