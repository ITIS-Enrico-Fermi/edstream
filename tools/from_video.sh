#!/bin/bash

video=$1;
start=$2;
stop=$3;

if [ -e $video ]; then
	for i in $(seq $start $stop); do
		python frame_from_video.py -s $video -f $i | python to_bitmap.py | python rotate_pixel.py | python bitmap_over_fifo.py;
		sleep 0.00001;
	done
else
	echo "file doesn't exist";
fi

