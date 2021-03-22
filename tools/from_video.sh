#!/bin/bash

video=$1

if [ -e $video ]; then
	for i in {10..30}; do
		python frame_from_video.py -s $video -f $i | python to_bitmap.py | python rotate_pixel.py | python bitmap_over_fifo.py;
		sleep 1;
	done
else
	echo "file doesn't exist";
fi

