#!/bin/bash 
for (( i=0; i<10; i++))
do  
  argo submit video.yaml --serviceaccount argo-loop -p knative_url=10.102.102.237 -n argo
  sleep 300 
done
