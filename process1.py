#!/usr/bin/env python3

import os
import pretty_midi

import pandas as pd

from shutil import copy2

#--------------------------------------------------
# HI, WELCOME TO THE AI-DATABASE-CREATOR SCRIPT   |
#--------------------------------------------------

# TRAIN-TEST SPLIT: marking this for not-training (ie testing)--------
trainers = {'Scarlatti' : ['k213.mid', 'k510.mid', 'k332.mid',
 'scark11.mid'],
'Sor' : ['sor_gs.mid', '12sor.mid', 'sstud17.mid', 'sorop60.mid'],
'Bach' : ['bjsfnem4.mid', 'preludn2.mid', 'wtc2231.mid',
 'bjsfncp3.mid'],
'Vivaldi' : ['vivcon6.mid', 'rv310_1.mid', '611_4.mid',
 'vivcfob1.mid'],
'Stravinsky' : ['lmstpet1.mid', 'stralcd4.mid', 'strlh_05.mid',
 'variatio.mid'],
'Haendel' : ['12piec2.mid', 'gfhktz02.mid', 'water14.mid',
 '6_air.mid'],
'Liszt' : ['01pasali.mid', '3mephis.mid', 'wildejag.mid',
 'kinglear.mid'],
'Haydn' : ['haydngq5.mid', 'trio3.mid', 'hydtr_1.mid',
 'nelson03.mid'] }
#---------------------------------------------------------------------

def initialize(n):
  midi_data = pretty_midi.PrettyMIDI(n)
  instruments = []
  for x in midi_data.instruments:
    instruments.append(x.notes)
  return instruments

def main(name):
  l = initialize(name)
  cols = {}
  for i,y in enumerate(l):
    for x in y:
      # we are NOT extracting the type of instrument,
      # and that is arguably an important feature
      cols['start'] = cols.get('start',[]) + [x.start]
      cols['end'] = cols.get('end',[]) + [x.end]
      cols['pitch'] = cols.get('pitch',[]) + [x.pitch]
      cols['velocity'] = cols.get('velocity',[]) + [x.velocity]
      cols['track'] = cols.get('track',[]) + [i]
  data = pd.DataFrame(cols)
  d = data

  return d

def creator(st):
  """
  create and don't error
  if directory existed
  """
  try:
    os.mkdir(st)
  except OSError as exc:
    if exc.errno != errno.EEXIST:
      raise Exception("ERROR: probably permission denied"\
                                   " for folder-creation")
    pass


def multiproc():
  composers = [x for x in os.listdir("raw_data") if os.path.isdir(x)]
  lar = len(composers)
  i_ = 1
  creator('AI_data')
  for x_ in composers:
    creator('AI_data/'+x_)
    for y_ in os.listdir(x_):
      try: 
        # populate new dir with both .MID and .csv files
        if y_ in trainers[x_]:
          # specially separating the ones used for testing
          creator('AI_data/'+x_+'nottrain')
          TEMP = 'AI_data/'+x_+'/nottrain'            
        else: TEMP = 'AI_data/'+x_
        main('raw_data/'+x_+'/'+y_).to_csv(TEMP+'/'+y_[:-3]+'.csv',
                                                        index=False)
        copy2('raw_data/'+x_+'/'+y_,TEMP+'/'+y_)       
      except Exception as ins:
        print('ERROR: ',ins.args)
        print('x_ and y_ are: ',x_,y_)
    print(f'ENDED {i_} of {lar}')
    i_ += 1
  return print('PROCESS ENDED!')
  
if __name__=='__main__':  
  print('ABOUT TO CREATE THE DATABASE!')
  multiproc()   

