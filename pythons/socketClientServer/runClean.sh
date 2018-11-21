#!/bin/bash
# Copyright  2014-2015  David Snyder
#                       Daniel Povey
# Apache 2.0.
#
# This script runs the NIST 2007 General Language Recognition Closed-Set
# evaluation.


targetDir=$1


function clean_dir(){
    for file in `ls $1`
    do
        if [ -d $1"/"$file ]  
        then
            rm -r $1"/"$file
        else
            if [ $file == "score.pd" ]
            then
                echo $file
            else
                rm -rf $1"/"$file
            fi
        fi
    done
}


clean_dir $targetDir
