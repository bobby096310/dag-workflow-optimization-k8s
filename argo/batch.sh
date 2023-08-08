#!/bin/bash 
for (( i=0; i<10; i++))
do  
  argo submit ~/argo/video.yaml --serviceaccount argo-loop -p knative_url=10.98.241.120 -n argo
  sleep 420 
done
