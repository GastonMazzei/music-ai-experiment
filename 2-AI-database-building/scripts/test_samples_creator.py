import pandas as pd
import os
import sys
from maker import *

def testing_main():
  times = {
        'Haendel':{'12piec2':[0, 20, 40, 60]},
        'Liszt':{'01pasali':[0, 20, 40, 60]},
        'Stravinsky':{
            'stralcd4':[0, 20, 40, 60],
            'variatio':[0, 20, 40, 60]},
        'Vivaldi':{
            '611_4':[0, 20, 10, 30]},
                                     }
  data = {}
  for x in [x for x in os.listdir() if (os.path.isdir(x) and
                                             x!='__pycache__')]:
    try:
      data[x] = []
      for y in [y[:-4] for y in os.listdir(f'{x}/nottrain') if (
                            y[-3:]=='csv' and 'DATA' not in y)]:
        print(f'arrived to {y}')
        flag = [0, 20, 40, 60]
        if times.get(x,False):
          if times[x].get(y,False):
            flag = times[x][y]
        data[x] += testing_process(
                  f'{x}/nottrain/{y}.csv',
                  flag,
                      )                       
      print(f'LEN {len(data[x])} and content {type(data[x][0])}')
      print(f'and inner shapes: {[K.shape for K in data[x]]}')
      build_new(data[x],f'TEST-{x.upper()}',y,f'{x}/nottrain',maxcols=sys.argv[1])
    except Exception as ins:
     print(ins.args)
     del(data[x])      

  return

def testing_process(df_name, time_info):
  specific_times = False
  try: 
    print(f'INPUT:"{sys.argv[2]}" making us overwrite poll-times')
    return extract_seven(df_name)
  except IndexError:
    return extract_seven(df_name, time_info)


if __name__=='__main__':
  print('STARTING')
  print('remove old ones...')
  not_existing = 0
  for x in [x for x in os.listdir() if (os.path.isdir(x) and
                                             x!='__pycache__')]:
    try: 
      os.system(f'rm {x}/nottrain/DATA-TEST-{x.upper()}.csv')
    except:
      not_existing += 1
  print('done!')
  if not_existing: print(f'In {not_existing} cases there were no'\
                                               ' "old" to remove')
  print('creating new ones...')
  testing_main()
  print('ENDED')
