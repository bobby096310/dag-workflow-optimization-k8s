#!/bin/bash
mc rm --recursive --force  myminio/bucket1/Video_Frames_Step/ --older-than 10m
mc rm --recursive --force  myminio/bucket1/Video_Chunks_Step/ --older-than 10m
mc rm --recursive --force  myminio/bucket1/Detected_Objects/ --older-than 10m
