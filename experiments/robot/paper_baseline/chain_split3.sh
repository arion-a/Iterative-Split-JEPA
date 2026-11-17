#!/bin/bash
# on the pod: E66. Per task: convert (paper format), train the three-head encoder (paper's epochs), embed, pack.
cd /workspace/work
[ -d data/robot/PickCube ] || tar xf ../data_PickCube.tar
[ -d data/robot/PushCube ] || tar xf ../data_PushCube.tar
for T in PickCube PushCube; do [ -d robot/data/$T-v1_hshared100 ] || python3 paper_baseline/make_paper_format.py $T data/robot robot/data > ../logs/convert_$T.log 2>&1; done
for TE in "PickCube 200" "PushCube 100"; do
  set -- $TE; T=$1; E=$2
  PYTHONUNBUFFERED=1 python3 paper_baseline/train_split3.py $T $E > ../logs/split3_$T.log 2>&1
  CK=$(find robot/experiments -name encoder.pt -path "*$(echo $T | tr 'A-Z' 'a-z')_split3*" | head -1)
  python3 paper_baseline/embed_three.py $T $CK > ../logs/embed3_$T.log 2>&1
  tar cf ../artifacts3_$T.tar data/robot_split3/feat/$T data/robot_split3/$T $CK $(dirname $CK)/metrics.json
  echo DONE > ../logs/done3_$T.txt
done
