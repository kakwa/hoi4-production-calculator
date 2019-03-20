#!/bin/sh
for i in light medium modern super_heavy;
do
	for t in armor sp_anti_air_brigade sp_artillery_brigade tank_destroyer_brigade;
	do
		cp heavy_${t}.svg ${i}_${t}.svg
	done
done
