#!/bin/bash
for (( i=0; i<5; i++))
do
	python3 test.py run video 3 1 1 1 F 1
	kubectl delete pods --all
	python3 test.py run video 3 1 1 1 T 1
	kubectl delete pods --all
done
