import os
import json
import time

import numpy
import numpy as np
from flask import Request
from minio import Minio
from numpy import array
from parliament import Context

from utils import *

client = Minio(os.environ.get('minio_url'), access_key=os.environ.get('minio_user'), secret_key=os.environ.get('minio_password'), secure=False)
bucket_name = os.environ.get('bucketName')


def upload_matrix(A, filename):
    numpy.savetxt("/tmp/" + filename, A)
    client.fput_object(bucket_name, "ChatBotData/" + filename, "/tmp/" + filename)


def upload_BOW(BOW):
    with open('/tmp/bos.txt', 'w') as f:
        for word in BOW:
            f.write(word + '\n')
    f.close()
    client.fput_object(bucket_name, "ChatBotData/" + 'bos.txt', '/tmp/bos.txt')


def mainFunc(filename, event):
    network_bound = event["network_bound"]
    start_time = int(round(time.time() * 1000))
    data = []
    with open(filename, 'r') as file:
        data = file.read().replace('\n', '')

    j_data = json.loads(data)
    all_unique_words = []

    all_intents = []
    for v in range(len(j_data["intents"])):
        newIntent = {}
        newIntent["name"] = j_data["intents"][v]["intent"]
        newIntent["data"] = j_data["intents"][v]["text"]
        newIntent["data"].extend(j_data["intents"][v]["responses"])
        for utterance in newIntent["data"]:
            words_list = utterance.split(" ")
            all_unique_words.extend(words_list)
        all_intents.append(newIntent)
        # print(newIntent)
        # print("*************")
        # print("*************")
    BOW = set(all_unique_words)
    All_matrices = []
    for newIntent in all_intents:
        print(newIntent["name"])
        list_vectors = []
        for utterance in newIntent["data"]:
            words_list = utterance.split(" ")
            vector = [int(w in words_list) for w in BOW]
            # print(vector)
            list_vectors.append(vector)
        A = array(list_vectors)
        All_matrices.append(A)

    end_time = int(round(time.time() * 1000))
    print("duration before upload:" + str(end_time - start_time))

    returnedDic = {}
    returnedDic["detail"] = {}
    returnedDic["detail"]["indeces"] = []
    bundle_size = event["bundle_size"]
    list_of_inputs_to_bundle = []

    for mat_index in range(len(All_matrices)):
        positive_A = All_matrices[mat_index]
        negative_A = []
        if (mat_index > len(All_matrices) - 4):

            negative_A = All_matrices[0]
            negative_A = np.concatenate((negative_A, All_matrices[1]), axis=0)
            negative_A = np.concatenate((negative_A, All_matrices[2]), axis=0)

        else:
            negative_A = All_matrices[mat_index + 1]
            negative_A = np.concatenate((negative_A, All_matrices[mat_index + 2]), axis=0)
            negative_A = np.concatenate((negative_A, All_matrices[mat_index + 3]), axis=0)

        if (network_bound == 1):
            upload_matrix(positive_A, all_intents[mat_index]["name"] + "_pos.txt")
            upload_matrix(negative_A, all_intents[mat_index]["name"] + "_neg.txt")

        j = {"intent_name": all_intents[mat_index]["name"], "skew": event["skew"],
             "network_bound": event["network_bound"]}
        list_of_inputs_to_bundle.append(j)
        if (len(list_of_inputs_to_bundle) >= bundle_size):
            newDict = {}
            newDict["values"] = list_of_inputs_to_bundle
            end_time = int(round(time.time() * 1000))
            newDict["duration"] = end_time - start_time
            returnedDic["detail"]["indeces"].append(newDict)
            list_of_inputs_to_bundle = []

    upload_BOW(BOW)
    end_time = int(round(time.time() * 1000))
    if (len(list_of_inputs_to_bundle) > 0):
        newDict = {}
        newDict["values"] = list_of_inputs_to_bundle
        newDict["duration"] = end_time - start_time
        returnedDic["detail"]["indeces"].append(newDict)

    return returnedDic


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
        exeRet = mainFunc("Intent.json", context.request.get_json())
        everything = {"Result": exeRet, "Received": ret, "Sent": payload_print(context.request)}
        return everything, 200
    else:
        print("Empty request", flush=True)
        return "{}", 200

