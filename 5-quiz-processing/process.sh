#!/bin/bash

cd scripts
printf "\nAbout to process Quiz-raw-data...\n"
python3 quiz-processor.py >/dev/null 2>&1
printf "\n\nDONE!\n\n"
printf "results saved in ./processed and copied in ../6-results/data/\n"
