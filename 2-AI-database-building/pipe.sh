#!usr/env/bash

#------------variables explained--
# (SR)
# Sampling rate: SR/(7*4) notes/sec
SRdefault=720

# (TAU)
# Window sizes used for training
# and validation (7sec +- TAU)
TAUdefault=0
#-------------------------------

mssg="
\n\n
HEY! this script is run by 3/AI-processing!
Seeing this means you run it on your own.
This will yield the same results (i.e. build
the AI-database) but with VERBOSE MODE: ON
\n\n\n
"
echo $mssg
sleep 5

SR=${1:-$SR}
TAU=${2:-$TAUdefault}
unzip "works-by-composer.zip"
cd "works-by-composer"
python3 ../scripts/maker.py $SR $TAU
python3 ../scripts/joiner.py 0 $SR
python3 ../scripts/test_samles_creator.py $SR
python3 ../scripts/joiner.py 1 $SR
names=("total-train.csv" "test.csv" "val.csv" "tags.dat")
cp tags.dat "../3-AI-processing/datasets/tags.dat"
cp tags.dat "../5-quiz-processing/scripts/tags.dat"
cp tags.dat "../6-results/data/tags.dat"

for f in ${names[@]}
do
  mv $f "../3-AI-processing/datasets/$f"
  echo "Sucessfully created the dataset $f in 3-AI-processing/datasets!"
done


