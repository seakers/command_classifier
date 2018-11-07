#!/usr/bin/env bash

for dir in runs/checkpoints/*/
do
    sed -i.bak "s|$PWD/runs/checkpoints|/home/ubuntu/daphne_brain/daphne_API/models|" ${dir}checkpoint
done

scp -i $DAPHNE_KEY -r runs/checkpoints/* ubuntu@13.58.54.49:~/daphne_brain/daphne_API/models

for f in runs/checkpoints/*/*.bak; do
    mv -- "$f" "${f%.bak}"
done