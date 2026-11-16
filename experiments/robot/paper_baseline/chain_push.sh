#!/bin/bash
# on the pod: PushCube only, paper's full setting (200 epochs): train, embed + ladder, pack artifacts.
cd /workspace/work
[ -d data/robot/PushCube ] || tar xf ../data_PushCube.tar
T=PushCube
[ -d robot/data/$T-v1_hshared100 ] || python3 paper_baseline/make_paper_format.py $T data/robot robot/data > ../logs/convert_$T.log 2>&1
PYTHONUNBUFFERED=1 python3 paper_baseline/train_paper.py $T 200 > ../logs/train_$T.log 2>&1
CK=$(find robot/experiments -name encoder.pt -path "*$(echo $T | tr 'A-Z' 'a-z')_paper*" | head -1)
python3 paper_baseline/embed_and_ladder.py $T $CK > ../logs/ladder_$T.log 2>&1
tar cf ../artifacts_$T.tar data/robot_paper/feat/$T data/robot_paper/$T $CK $(dirname $CK)/metrics.json results/paper_baseline/${T}_paper_fixed_slice.json
echo DONE > ../logs/done_$T.txt
