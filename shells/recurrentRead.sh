#! /bin/bash

srcDir=$1
targetDir=$2

function read_dir(){
    for file in `ls $1`
    do
        if [ -d $1"/"$file ]  
        then
            read_dir $1"/"$file
        else
            echo $1"/"$file
        fi
    done
}

function cp_dir(){
    if [ ! -d $2 ]
    then
        mkdir -p $2
    fi

    for file in `ls $1`
    do
        if [ -d $1"/"$file ]
        then
            cp_dir $1"/"$file $2"/"$file
        else
            ext=${file##*.}
            if [ $ext == "o" ]
            then
                echo $1"/"$file
            elif [ $ext == "cc" ]
            then
                echo $1"/"$file
            elif [ $ext == "cpp" ]
            then
                 echo $1"/"$file
                 
            else
                cp $1"/"$file $2"/"$file
            fi
        fi
    done
}

cp_dir $srcDir $targetDir
