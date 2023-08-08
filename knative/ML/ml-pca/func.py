import os
import json
import time

from numpy import array
from numpy import mean
from numpy import cov
from numpy.linalg import eig
from numpy import genfromtxt
from numpy import concatenate
from numpy import savetxt
import numpy as np

from minio import Minio
from utils import *
from parliament import Context

def mainFunc(event):
    if ('dummy' in event) and (event['dummy'] == 1):
        print("Dummy call, doing nothing")
        return

    client = Minio(os.environ.get('minio_url'), access_key=os.environ.get('minio_user'), secret_key=os.environ.get('minio_password'), secure=False)
    bucket_name = os.environ.get('bucketName')
    client.fget_object(bucket_name, "ML_Pipeline/Digits_Test_Small.txt", "/tmp/Digits_Test.txt")
    print("Init download ###########################")

    start_time = int(round(time.time() * 1000))

    start_download = int(round(time.time() * 1000))
    filename = "/tmp/Digits_Train_Org.txt"
    client.fget_object(bucket_name, "ML_Pipeline/Digits_Train_org.txt", filename)
    end_download = int(round(time.time() * 1000))

    start_process = int(round(time.time() * 1000))

    train_data = genfromtxt('/tmp/Digits_Train_Org.txt', delimiter='\t')

    train_labels = train_data[:, 0]

    A = train_data[:, 1:train_data.shape[1]]

    # calculate the mean of each column
    MA = mean(A.T, axis=1)

    # center columns by subtracting column means
    CA = A - MA

    # calculate covariance matrix of centered matrix
    VA = cov(CA.T)

    # eigendecomposition of covariance matrix
    values, vectors = eig(VA)

    # project data
    PA = vectors.T.dot(CA.T)

    np.save("/tmp/vectors_pca.txt", vectors)

    first_n_A = PA.T[:, 0:100].real
    train_labels = train_labels.reshape(train_labels.shape[0], 1)

    first_n_A_label = concatenate((train_labels, first_n_A), axis=1)

    savetxt("/tmp/Digits_Train_Transform.txt", first_n_A_label, delimiter="\t")

    end_process = int(round(time.time() * 1000))

    start_upload = int(round(time.time() * 1000))
    client.fput_object(bucket_name, "ML_Pipeline/vectors_pca.txt", "/tmp/vectors_pca.txt.npy")
    client.fput_object(bucket_name, "ML_Pipeline/train_pca_transform_2.txt", "/tmp/Digits_Train_Transform.txt")

    end_upload = int(round(time.time() * 1000))
    end_time = int(round(time.time() * 1000))

    subfilename = "PCA_" + event['key1'] + "_start_" + str(start_time) + "_end_" + str(end_time)
    filename = "/tmp/" + subfilename
    f = open(filename, "w")
    f.write(filename)
    f.close()
    client.fput_object(bucket_name, "ML_Pipeline/LightGBM_Times/", filename)
    bundle_size = event['bundle_size']
    list_hyper_params = []
    all_runs = 4 * 4 * 4

    for feature_fraction in [0.25, 0.5, 0.75, 0.95]:
        max_depth = 10
        for num_of_trees in [5, 10, 15, 20]:
            list_hyper_params.append((num_of_trees, max_depth, feature_fraction))

    returnedDic = {}
    returnedDic["detail"] = {}
    returnedDic["detail"]["indeces"] = []

    num_of_trees = []
    max_depth = []
    feature_fraction = []
    num_bundles = 0
    count = 0
    for tri in list_hyper_params:
        feature_fraction.append(tri[2])
        max_depth.append(tri[1])
        num_of_trees.append(tri[0])
        count += 1
        if (count >= bundle_size):
            count = 0
            num_bundles += 1
            j = {"mod_index": num_bundles, "PCA_Download": (end_download - start_download),
                 "PCA_Process": (end_process - start_process), "PCA_Upload": (end_upload - start_upload),
                 "key1": "inv_300", "num_of_trees": num_of_trees, "max_depth": max_depth,
                 "feature_fraction": feature_fraction, "threads": 6}
            num_of_trees = []
            max_depth = []
            feature_fraction = []
            returnedDic["detail"]["indeces"].append(j)

    print(returnedDic)
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
        exeRet = mainFunc(context.request.get_json())
        everything = {"Result": exeRet, "Received": ret, "Sent": payload_print(context.request)}
        return everything, 200
    else:
        print("Empty request", flush=True)
        return "{}", 200

