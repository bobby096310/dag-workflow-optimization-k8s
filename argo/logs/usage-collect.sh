#!/bin/bash 
for (( i=0; i<15; i++))
do
  date >> top.txt
  kubectl top pods >> top.txt
  kubectl top nodes >> top.txt
  sleep 15
done
