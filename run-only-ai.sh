#!/env/bash

welcome="
\nWelcome to the ONLY-AI mode of the humans_VS_AI-based-classifiers mini-project

This script will skip creating a Quiz for you to publish, and instead will use
the results of the original Online-Quiz ('./5-quiz-processing/raw-data/...').
The files are public and (by september 2020) are being daily updated at 'shorturl.at/lyKS7'
The data collection will end at Oct-2020
more info: https://github.com/GastonMazzei/music-ai-experiment\n\n
"

printf "$welcome"
printf "\n\n----------(1)---------------\nMAKE AI-PREDICTIONS\n\n\n"
(cd "3-AI-processing"; bash "process.sh")
printf "\n\n----------(2)---------------\nGATHER HUMAN PREDICTIONS\n\n\n"
(cd "5-quiz-processing"; bash "process.sh")
printf "\n\n----------(3)---------------\nCOMPARE HUMANS VS AI\n\n\n"
(cd "6-results"; bash "generate_results.sh")
printf "SCRIPT ENDED:\n"
printf "RESULTS are in './6-results/RESULTS/RESULTS.png'!!!\n"
