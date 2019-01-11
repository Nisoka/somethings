#!/bin/bash
# Copyright  2014-2015  David Snyder
#                       Daniel Povey
# Apache 2.0.
#
# This script runs the NIST 2007 General Language Recognition Closed-Set
# evaluation.
curDir=`pwd`
cd /home/liujunnan/git-nan/code/kaldi-master/egs/langRec/V2

# =====================================
# runTest.sh 
#!/bin/bash
# Copyright  2014-2015  David Snyder
#                       Daniel Povey
# Apache 2.0.
#
# This script runs the NIST 2007 General Language Recognition Closed-Set
# evaluation.

cmd=run.pl
. cmd.sh
set -e

nj=8

if [ -f path.sh ]; then . ./path.sh; fi
. parse_options.sh || exit 1;



if [ $# -ne 3 ];
then
    echo  "parameters is not enough :" $#
    exit 1
fi

sysroot=/data/sr-data/langRecSys

expdir=$sysroot/exp
classifyModelDir=$sysroot/modelsForAll
# classifyModelUse=XGBoost
classifyModelUse=PLDA
enrollDir=$sysroot/exp/processedVectors/train


stage=$1
target=$2
# target will have the bellow files will be ok!
# Bnfeatures.scp, Note the name
# utt2spk
# utt2lang
outDir=$3

if [ ! -f $classifyModelDir/labelList ]
then
    echo "classify ModelDir does not have the classout labelList"
    exit 0
fi


# -------------- export the $eerdata $traindata to cur env

function PrepareDir() {
    
    srcDir_=$1
    featscp_=$2

    utt2spk=$srcDir_/utt2spk
    utt2lang=$srcDir_/utt2lang
    if [ -f $utt2spk ] ; then
        rm -f $utt2spk
        rm -f $utt2lang
    fi

    trials=$srcDir_/eer_trials
    if [ -f $trials ] ; then
        rm -f $trials
    fi

    

    labelList=`cat $classifyModelDir/labelList`
    cat $srcDir_/$featscp_ | while read line
    do
        lineArr=($line)
        utt=${lineArr[0]}
        featPath=${lineArr[1]}

        echo $utt $utt >> $utt2spk
        echo $utt zh >> $utt2lang
        
        for lang in $labelList
        do
            if [ $lang == "zh" ] ; then
                echo $lang $utt "target" >> $trials
            else
                echo $lang $utt "nontarget" >> $trials
            fi
        done
    done
}


function cleanBNF(){
    bnfscp=$1
    cat $bnfscp | while read line
    do
        # echo $line
        lineAry=($line)
        path=${lineAry[1]}
        rm -f $path
        # echo $path
    done
}



if [ $stage -le 0 ]
then
    echo "extract Test Features "
    echo ""
    mkdir -p $target/log 
    $cmd $target/log/ivector-copy-feats.log \
             ivector-copy-feats $target/Bnfeatures.scp ark,scp:$target/feats.ark,$target/feats.scp

    PrepareDir $target feats.scp
    
    cleanBNF $target/Bnfeatures.scp

    utils/fix_data_dir.sh $target
    
    cnt=`wc $target/Bnfeatures.scp`
    # echo "$target/Bnfeatures.scp $cnt"
    cntAry=($cnt)
    cnt=${cntAry[0]}
    if [ $cnt -lt $nj ]
    then
        nj=$cnt
    fi
fi

if [ $stage -le 1 ]
then
    echo "extract Test i-vector "
    echo ""

    isTrain=false
    srcDir=$target
    extractorDir=$expdir/extractor_2048
    ivectorDir=$target/ivectors
    processModelDir=$expdir/vectorProcessModels
    processVecDir=$target/processedVectors
    plda_data_dir=$sysroot/data/train
    local/extractIvector.sh \
        --nj $nj\
        $isTrain $srcDir $extractorDir $ivectorDir $processModelDir $processVecDir $plda_data_dir
fi


if [ $stage -le 2 ]
then
    isTrain=false
    dataDir=$target
    processedVecArk=$target/processedVectors/ivector.ark
    resultDir=$target/classifyResult
    mkdir -p $resultDir
    
    ./classifiers/runClassifier.sh \
        $isTrain $processedVecArk $dataDir $classifyModelDir $resultDir $classifyModelUse $enrollDir
fi

cp $resultDir/result${classifyModelUse}.score $outDir/score.pd

cd $curDir
./runClean.sh $outDir
