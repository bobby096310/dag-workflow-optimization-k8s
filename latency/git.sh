#!/bin/bash
for (( i=0; i<100; i++))
do
	git add ./
	git commit -m "more data"
      	git push https://bobby096310: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@github.com/bobby096310/dag-workflow-optimization-k8s  	

sleep 600
done
