#!/bin/bash
# runs on the pod: Push data, wait for Pick training, then Push training in parallel with Pick embedding + ladder
cd /workspace/work
tar xf ../data_PushCube.tar && python3 paper_baseline/make_paper_format.py PushCube data/robot robot/data > ../logs/push_convert.log 2>&1
while ! grep -q "^DONE" ../logs/pick_train.log; do sleep 15; done
PYTHONUNBUFFERED=1 nohup python3 paper_baseline/train_paper.py PushCube 30 > ../logs/push_train.log 2>&1 &
CK=$(find robot/experiments -name encoder.pt -path "*pickcube_paper*" | head -1)
python3 paper_baseline/embed_and_ladder.py PickCube $CK > ../logs/pick_ladder.log 2>&1
while ! grep -q "^DONE" ../logs/push_train.log; do sleep 15; done
CK=$(find robot/experiments -name encoder.pt -path "*pushcube_paper*" | head -1)
python3 paper_baseline/embed_and_ladder.py PushCube $CK > ../logs/push_ladder.log 2>&1
echo ALLDONE > ../logs/alldone.txt
