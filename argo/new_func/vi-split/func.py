#!/usr/bin/env python
import os
import json
import sys
from minio import Minio
import subprocess
import re
import time
from utils import *
from parliament import Context

FFMPEG_STATIC = "var/ffmpeg"

length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_length = re.compile(length_regexp)

def mainFunc(event, minio_url, minio_user, minio_password):
    if ('dummy' in event) and (event['dummy'] == 1):
        print(bucketName)
        print("Dummy call, doing nothing")
        return

    # print(subprocess.call([FFMPEG_STATIC]))

    client = Minio(minio_url, access_key=minio_user, secret_key=minio_password, secure=False)
    bucket_name = "bucket1"
    
    filename = "/tmp/src.mp4"
    #print(event)
    src_video = event['src_name']
    DOP = int(event['DOP'])
    detect_prob = int(event['detect_prob'])
    client.fget_object(bucket_name, "Video_Src/min_" + src_video + ".mp4", filename)

    output = subprocess.Popen(FFMPEG_STATIC + " -i '" + filename + "' 2>&1 | grep 'Duration'",
                              shell=True,
                              stdout=subprocess.PIPE
                              ).stdout.read().decode("utf-8")

    #print(output)
    matches = re_length.search(output)
    count = 0
    millis_list = []
    if matches:
        video_length = int(matches.group(1)) * 3600 + \
                       int(matches.group(2)) * 60 + \
                       int(matches.group(3))
        #print("Video length in seconds: " + str(video_length))

        start = 0
        chunk_size = 2  # in seconds
        while (start < video_length):
            end = min(video_length - start, chunk_size)
            millis = int(round(time.time() * 1000))
            millis_list.append(millis)
            chunk_video_name = 'min_' + src_video + "_" + str(count) + "_" + str(millis) + '.mp4'
            subprocess.call([FFMPEG_STATIC, '-i', filename, '-ss', str(start), '-t', str(end), '-c', 'copy',
                             '/tmp/' + chunk_video_name])

            count = count + 1
            start = start + chunk_size
            client.fput_object(bucket_name, "Video_Chunks_Step/" + chunk_video_name, "/tmp/" + chunk_video_name)

    #print("Done!")

    payload = count / DOP
    listOfDics = []
    currentList = []
    currentMillis = []
    for i in range(count):
        if len(currentList) < payload:
            currentList.append(i)
            currentMillis.append(millis_list[i])
        if len(currentList) == payload:
            tempDic = {}
            tempDic['values'] = currentList
            tempDic['source_id'] = src_video
            tempDic['millis'] = currentMillis
            tempDic['detect_prob'] = detect_prob
            listOfDics.append(tempDic)
            currentList = []
            currentMillis = []

    '''
    returnedObj = {
        "detail": {
            "indeces": listOfDics
        }
    }
    #print(returnedObj)
    '''
    return listOfDics

def main():
    args = sys.argv[1:]
    input = json.loads(args[0])
    minio_url = args[1]
    minio_user = args[2]
    minio_password = args[3]
    result = mainFunc(input, minio_url, minio_user, minio_password)
    print(json.dumps(result))
    return result

if __name__ == "__main__":
    main()
