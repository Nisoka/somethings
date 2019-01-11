#!/bin/env python

recSysDir = "/home/liujunnan/langRec"

workDir = recSysDir +  "/Result"
wavDir = recSysDir +  "/wav"

testDir = "/home/liujunnan/langRec/test"

nnPath = "/home/liujunnan/git-nan/code/pytools/BUT-Speech/BottleneckFeatureExtractor/nn_weights/"

LRConfig = {
    "pairSplit":"  ",
    "bnfOutDir": workDir+ "/bnf",
    "iveOutDir": workDir + "/ivector",
    "iveExtTempDir": workDir + "/ivecTemp",
    "dataDir": workDir + "/data",
    "batchCntLimit":15,
    "batchTime": 20,
    "kaldiProcessLimit":2,
    "kaldiNj":3,
    "extractBNFLimit":1,
}

# Server
# 600: 400(s) (63s)
# "batchTime": 10,
# "kaldiProcessLimit":8,
# "kaldiNj":8,
# "extractBNFLimit":8,
# BNF -> IVECT 80 BNF Block wait

# Server
# 600: 510(s) (63s)
# "batchTime": 10,
# "kaldiProcessLimit":6,
# "kaldiNj":8,
# "extractBNFLimit":3,
# BNF -> IVECTOR 80 BNF wait

# Server
# 600: 600(s) (45s)
# "batchTime": 10,
# "kaldiProcessLimit":6,
# "kaldiNj":8,
# "extractBNFLimit":2,
# BNF -> IVECTOR 40 BNF wait



# NUC-7 one machine
# 600: 1028(s) *(18s)* (return 593)
# "batchCntLimit":15,   ---- max 15
# "batchTime": 20,      ---- batch limit time 20s
# "kaldiProcessLimit":2, --- kaldi Step 2
# "kaldiNj":3,           --- kaldi nj 3
# "extractBNFLimit":1,   --- BNF keep one process

# NUC-5 one machine
# 600: 1100(s) *(18s)* (return 567)
# "batchCntLimit":15,   ---- max 15
# "batchTime": 20,      ---- batch limit time 20s
# "kaldiProcessLimit":2, --- kaldi Step 2
# "kaldiNj":3,           --- kaldi nj 3
# "extractBNFLimit":1,   --- BNF keep one process
