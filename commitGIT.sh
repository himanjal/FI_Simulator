#!/bin/bash

message=$1

rm *.pyc
git add .
git commit -m "$message"
git pull
git push origin master