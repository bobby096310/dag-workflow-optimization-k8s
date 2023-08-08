#!/usr/bin/env python

import json
import os
from minio import Minio
import subprocess
import time
from utils import *
from parliament import Context

FFMPEG_STATIC = "var/ffmpeg"


def mainFunc(event):
    if('dummy' in event) and (event['dummy'] == 1):
       print("Dummy call, doing nothing")
       return {"Extract Got Dummy" : "Dummy call, doing nothing"}

    #print(subprocess.call([FFMPEG_STATIC]))
    client = Minio(os.environ.get('minio_url'), access_key=os.environ.get('minio_user'), secret_key=os.environ.get('minio_password'), secure=False)
    bucket_name = os.environ.get('bucketName')
    print(event)
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
    print("Done!") 

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

def main(context: Context):
    """
    Function template
    The context parameter contains the Flask request object and any
    CloudEvent received with the request.
    """

    # Add your business logic here
    print("Received request")

    if 'request' in context.keys():
        ret = pretty_print(context.request)
        print(ret, flush=True)
        exeRet = mainFunc(context.request.get_json())
        everything = {"Result": exeRet, "Received": ret, "Sent": payload_print(context.request)}
        return everything, 200
    else:
        print("Empty request", flush=True)
        return "{}", 200

