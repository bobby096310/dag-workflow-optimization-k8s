#!/usr/bin/env python

import json
import os
import sys
from minio import Minio
import subprocess
import time
from utils import *
from parliament import Context

FFMPEG_STATIC = "var/ffmpeg"


def mainFunc(event, minio_url, minio_user, minio_password):
    if('dummy' in event) and (event['dummy'] == 1):
       print("Dummy call, doing nothing")
       return {"Extract Got Dummy" : "Dummy call, doing nothing"}

    #print(subprocess.call([FFMPEG_STATIC]))
    client = Minio(minio_url, access_key=minio_user, secret_key=minio_password, secure=False)
    bucket_name = "bucket1"
    #print(event)
    list_of_chunks = event['values']
    src_video = event['source_id']
    millis_list = event['millis']
    detect_prob = event['detect_prob']
    count=0
    extract_millis = []
    for record in list_of_chunks:
        filename = "/tmp/chunk_" + str(record) + ".mp4"
        key = "Video_Chunks_Step/min_"+str(src_video)
        key = key +"_"+str(record)+"_"
        key = key + str(millis_list[count])+".mp4"
        count = count + 1
        client.fget_object(bucket_name, key, filename)
        millis = int(round(time.time() * 1000))
        extract_millis.append(millis)

        frame_name = key.replace("Video_Chunks_Step/","").replace("min", "frame").replace(".mp4","_" + str(millis) + ".jpg")
        subprocess.call([FFMPEG_STATIC, '-i', filename, '-frames:v', "1" , "-q:v","1", '/tmp/'+frame_name])
        try:
            client.fput_object(bucket_name, "Video_Frames_Step/"+frame_name, "/tmp/"+frame_name)
        except:
            client.fput_object(bucket_name, "Video_Frames_Step/"+frame_name, "var/Frame_1.jpg")
    #print("Done!") 

    obj= {
        'statusCode': 200,
        'counter': count,
        'millis1': millis_list,
        'millis2': extract_millis,
        'source_id': src_video,
        'detect_prob': detect_prob,		
        'values': list_of_chunks,
        'body': json.dumps('Download/Split/Upload Successful!'),
        
    }
    #print(obj)
    return obj

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


