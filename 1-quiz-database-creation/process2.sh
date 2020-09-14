#!/bin/bash

mkdir -p poll_data

declare -a arrayscarlatti=("k213" "k510" "k332" "scark11")
declare -a arraysor=("sor_gs" "12sor" "sstud17" "sorop60")
declare -a arraybach=("bjsfnem4" "preludn2" "wtc2231" "bjsfncp3")
declare -a arrayvivaldi=("vivcon6" "rv310_1" "611_4" "vivcfob1")
map=(["Scarlatti"]=arrayscarlatti ["Sor"]=arraysor ["Bach"]=arraybach ["Vivaldi"]=arrayvivaldi)
declare -a keys=("Scarlatti" "Sor" "Bach" "Vivaldi")

L=${#keys[@]}
for (( j=1; j<${L}+1; j++ ));
do
  compo=${keys[$j-1]}
  f1="AI_data/$compo/nottrain"
  f2="poll_data/$compo"
  mkdir -p $f2
  declare -a array=${map[${keys[$j-1]}]}
  arraylength=${#array[@]}
  for (( i=1; i<${arraylength}+1; i++ ));
  do
    echo $i " / " ${arraylength} " : " ${array[$i-1]}
    name=${array[$i-1]} 
    mkdir -p $f2
    timidity "$f1/$name.mid" -Ow -o - | ffmpeg -i - -acodec libmp3lame -ab 64k "$f2/song.mp3"
    names=([0]="a" [20]="b" [40]="c" [75]="d")
    for t in 0 20 40 75
    do
      ffmpeg -ss $t -i "$f2/song.mp3" -t 7 -c copy "$f2/$name${names[$t]}.mp3"
    done
    rm "$f2/song.mp3"
  done
done


declare -a arraystravinsky=("lmstpet1" "stralcd4" "strlh_05" "variatio")
declare -a arrayhaendel=("12piec2" "gfhktz02" "water14" "6_air")
declare -a arrayliszt=("01pasali" "3mephis" "wildejag" "kinglear")
declare -a arrayhaydn=("haydngq5" "trio3" "hydtr_1" "nelson03")
map=(["Stravinsky"]=arraystravinsky ["Haendel"]=arrayhaendel ["Liszt"]=arrayliszt ["Haydn"]=arrayhaydn)
declare -a keys=("Stravinsky" "Haendel" "Liszt" "Haydn")

L=${#keys[@]}
for (( j=1; j<${L}+1; j++ ));
do
  compo=${keys[$j-1]}
  f1="AI_data/$compo/nottrain"
  f2="poll_data/$compo"
  mkdir -p $f2
  declare -a array=${map[${keys[$j-1]}]}
  arraylength=${#array[@]}
  for (( i=1; i<${arraylength}+1; i++ ));
  do
    echo $i " / " ${arraylength} " : " ${array[$i-1]}
    name=${array[$i-1]} 
    mkdir -p $f2
    timidity "$f1/$name.mid" -Ow -o - | ffmpeg -i - -acodec libmp3lame -ab 64k "$f2/song.mp3"
    names=([0]="a" [20]="b" [40]="c" [75]="d")
    for t in 0 20 40 75
    do
      ffmpeg -ss $t -i "$f2/song.mp3" -t 7 -c copy "$f2/$name${names[$t]}.mp3"
    done
    rm "$f2/song.mp3"
  done
done

im="${PWD}/image.png"
refs="${PWD}/poll_data/refs.dat" 
mkdir -p "poll_data/samples"
i=1
for f in *
do
  if [[ -d $f ]]; then
    cd $f
    for k in *
    do
      ffmpeg -loop 1 -i $im -i $k -c:a copy -c:v libx264 -shortest "poll_data/samples/CMExpert_random-sample-$i.mp4"
      touch $refs
      echo "$i $f $k" >> $refs
      i=$((i + 1))
    done
    cd ..
  else
    echo "$f is not a folder"
  fi
done


#repair script for Haendel & Liszt
# cases that DIDNT lasted >= 75+7 secs

songs=(["Liszt"]="pasali01" ["Haendel"]="12piec2")
declare -a comps=("Haendel" "Liszt")
arraylength=${#comps[@]}
for (( i=1; i<${arraylength}+1; i++ ));
do  
  comp=$comps[i]
  work=$songs[$comps[i]]
  timidity "AI_data/$comp/nottrain/$work.mid" -Ow -o - | ffmpeg -i - -acodec libmp3lame -ab 64k "poll_data/$comp/song.mp3"
  names=([60]="d") 
  ffmpeg -ss 60 -i "poll_data/$comp/song.mp3" -t 7 -c copy "poll_data/$comp/${work}d.mp3" -y
  rm "poll_data/$comp/song.mp3"
done

name1="CMExpert_random-sample-52.mp4"
name0="01pasalid.mp3"
ffmpeg -loop 1 -i image.png -i "poll_data/Liszt/$name0" -c:a copy -c:v libx264 -shortest "poll_data/samples/$name1" -y
name1="CMExpert_random-sample-20.mp4"
name0="12piec2d.mp3"
ffmpeg -loop 1 -i image.png -i "poll_data/Haendel/$name0" -c:a copy -c:v libx264 -shortest "poll_data/samples/$name1" -y



# STRAVINSKY & VIVALDI cases 
# that didnt lasted 75+7 secs

#----combo 1
songs=(["Stravinsky"]="stralcd4")
numbers=(["Stravinsky"]="168")
declare -a comps=("Stravinsky")
arraylength=${#comps[@]}
for (( i=1; i<${arraylength}+1; i++ ));
do  
  comp=${comps[$i-1]}
  work=${songs[$comps[$i-1]]}
  timidity "AI_data/$comp/nottrain/$work.mid" -Ow -o - | ffmpeg -i - -acodec libmp3lame -ab 64k "poll_data/$comp/song.mp3"
  ffmpeg -ss 60 -i "poll_data/$comp/song.mp3" -t 7 -c copy "poll_data/$comp/${work}d.mp3" -y
  touch "poll_data/$comp/song.mp3" && rm "poll_data/$comp/song.mp3"
  name1="CMExpert_random-sample-${numbers[$comp]}.mp4"
  name0="${work}d.mp3"
  ffmpeg -loop 1 -i image.png -i "poll_data/$comp/$name0" -c:a copy -c:v libx264 -shortest "poll_data/samples/$name1" -y
done

#----combo 2
songs=(["Stravinsky"]="variatio") 
numbers=(["Stravinsky"]="176")
declare -a comps=("Stravinsky")
arraylength=${#comps[@]}
for (( i=1; i<${arraylength}+1; i++ ));
do  
  comp=${comps[$i-1]}
  work=${songs[$comps[$i-1]]}
  timidity "poll_data/$comp/nottrain/$work.mid" -Ow -o - | ffmpeg -i - -acodec libmp3lame -ab 64k "poll_data/$comp/song.mp3"
  ffmpeg -ss 60 -i "poll_data/$comp/song.mp3" -t 7 -c copy "poll_data/$comp/${work}d.mp3" -y
  touch "poll_data/$comp/song.mp3" && rm "poll_data/$comp/song.mp3"
  name1="CMExpert_random-sample-${numbers[$comp]}.mp4"
  name0="${work}d.mp3"
  ffmpeg -loop 1 -i image.png -i "poll_data/$comp/$name0" -c:a copy -c:v libx264 -shortest "poll_data/samples/$name1" -y
done


#----combo 3
songs=(["Vivaldi"]="611_4")
numbers=(["Vivaldi"]="179")
declare -a comps=("Vivaldi")
arraylength=${#comps[@]}
for (( i=1; i<${arraylength}+1; i++ ));
do  
  comp=${comps[$i-1]}
  work=${songs[$comps[$i-1]]}
  timidity "AI_data/$comp/nottrain/$work.mid" -Ow -o - | ffmpeg -i - -acodec libmp3lame -ab 64k "poll_data/$comp/song.mp3"
  ffmpeg -ss 10 -i "poll_data/$comp/song.mp3" -t 7 -c copy "poll_data/$comp/${work}c.mp3" -y
  touch "poll_data/$comp/song.mp3" && rm "poll_data/$comp/song.mp3"
  name1="CMExpert_random-sample-${numbers[$comp]}.mp4"
  name0="${work}c.mp3"
  ffmpeg -loop 1 -i image.png -i "poll_data/$comp/$name0" -c:a copy -c:v libx264 -shortest "poll_data/samples/$name1" -y
done

#----combo 3
songs=(["Vivaldi"]="611_4")
numbers=(["Vivaldi"]="180")
declare -a comps=("Vivaldi")
arraylength=${#comps[@]}
for (( i=1; i<${arraylength}+1; i++ ));
do  
  comp=${comps[$i-1]}
  work=${songs[$comps[$i-1]]}
  timidity "AI_data/$comp/nottrain/$work.mid" -Ow -o - | ffmpeg -i - -acodec libmp3lame -ab 64k "poll_data/$comp/song.mp3"
  ffmpeg -ss 30 -i "poll_data/$comp/song.mp3" -t 7 -c copy "poll_data/$comp/${work}d.mp3" -y
  touch "poll_data/$comp/song.mp3" && rm "poll_data/$comp/song.mp3"
  name1="CMExpert_random-sample-${numbers[$comp]}.mp4"
  name0="${work}d.mp3"
  ffmpeg -loop 1 -i image.png -i "poll_data/$comp/$name0" -c:a copy -c:v libx264 -shortest "poll_data/samples/$name1" -y
done


echo "ENDED!"
