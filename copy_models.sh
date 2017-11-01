#!/usr/bin/env bash

cp -a runs/checkpoints/. $1

for dir in $1/*/
do
    sed -i "s|$PWD/runs/checkpoints|$1|" ${dir}checkpoint
done