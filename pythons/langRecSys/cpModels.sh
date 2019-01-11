#!/bin/bash

src_sys=$1
tar_sys=$2
src_exp=$1/exp
tar_exp=$2/exp

rm -rf $tar_exp/extractor_2048
cp $src_exp/extractor_2048 -r $tar_exp/extractor_2048

rm -rf $tar_exp/vectorProcessModels
cp $src_exp/vectorProcessModels -r $tar_exp/vectorProcessModels


mkdir -p $tar_exp/processedVectors/train
cp $src_exp/processedVectors/train/ivector_mean.vec              $tar_exp/processedVectors/train
cp $src_exp/processedVectors/train/num_utts_ivector.ark          $tar_exp/processedVectors/train
copy-vector ark:$src_exp/processedVectors/train/lang_ivector.ark     ark:$tar_exp/processedVectors/train/lang_ivector.ark

rm -rf $tar_sys/modelsForAll
cp $src_sys/models-3-processed  -r $tar_sys/modelsForAll
