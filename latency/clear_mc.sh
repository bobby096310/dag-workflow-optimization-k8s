#!/bin/bash
for (( i=0; i<100; i++))
do
	mc rm --recursive --force  myminio/bucket1/Video_Frames_Step/ --older-than 10m
	mc rm --recursive --force  myminio/bucket1/Video_Chunks_Step/ --older-than 10m
	mc rm --recursive --force  myminio/bucket1/Detected_Objects/ --older-than 10m  
sleep 900
done
