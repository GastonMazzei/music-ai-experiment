#!/bin/bash

#_______________________________.
# metric could be also:         |
#                               |
# 'precision', 'f1', 'accuracy' |
#_______________________________|

METRIC="recall"
(cd data; python3 "../scripts/script.py" $METRIC)
printf "\n\nSUCCESSFULLY GENERATED RESULTS!\n\n"
eog "RESULTS/RESULTS.png"

