#!/bin/bash
# on the pod: convert both tasks, train both (30 epochs), embed, pack checkpoints + embeddings for download
cd /workspace/work
tar xf ../data_PickCube.tar; tar xf ../data_PushCube.tar
for T in PickCube PushCube; do python3 paper_baseline/make_paper_format.py $T data/robot robot/data > ../logs/convert_$T.log 2>&1; done
for T in PickCube PushCube; do
  PYTHONUNBUFFERED=1 python3 paper_baseline/train_paper.py $T 30 > ../logs/train_$T.log 2>&1
  CK=$(find robot/experiments -name encoder.pt -path "*$(echo $T | tr 'A-Z' 'a-z')_paper*" | head -1)
  python3 paper_baseline/embed_and_ladder.py $T $CK > ../logs/ladder_$T.log 2>&1
done
tar cf ../artifacts.tar data/robot_paper $(find robot/experiments -name encoder.pt) $(find robot/experiments -name metrics.json) results/paper_baseline
echo ALLDONE > ../logs/alldone.txt
