import os
import pandas as pd
import re
import sys

def tags_dict():
    with open('tags.dat','r') as f:
        tags_list = f.readlines()
    tags = {}
    key_pattern = re.compile('item:[ ]+([a-z]+)',re.I)
    item_pattern = re.compile('key:[ ]+([0-9]+)',re.I)
    for x in tags_list:
        tags[re.search(
             key_pattern, x
                    ).group(1).lower()] = re.search(
                                    item_pattern, x
                                              ).group(1)
    return tags

def building_call(optional_flag: False, MAXCOLS):
    #MAXCOLS = 4*1200# did worked 336*2!
    big_val = pd.DataFrame(columns=[str(x) for x in range(MAXCOLS+1)])
    if not optional_flag:
        # train-val
        big_train = big_val.copy()
        tags = {}
        counter = 0
        source = [x for x in os.listdir() if (os.path.isdir(x)
                                           and x not in ['__pycache__',
                                                         'scripts'])]
    else:
        tags = tags_dict()
        names = [x for x in os.listdir() if (os.path.isdir(x)
                                           and x not in ['__pycache__',
                                                         'scripts'])]
        source = [f'{x}/nottrain/DATA-TEST-{x.upper()}.csv' for x in names]
    for L in source:
        try:
            if not optional_flag:
                # train-val
                tags[L] = counter
                train = pd.read_csv(f'{L}/DATA-TRAIN.csv').iloc[:,1:]
                val = pd.read_csv(f'{L}/DATA-VALID.csv').iloc[:,1:]
                train[str(MAXCOLS)] = counter 
                val[str(MAXCOLS)] = counter 
                counter += 1
                big_val = pd.concat([big_val,val.iloc[:700,:]],axis=0)
                big_train = pd.concat([big_train,train],axis=0)
                print('REPORT FOR',L,':')
                print(f'length of train: {train.shape}\n '\
                         f'length of val: {val.shape}')
            else:
                val = pd.read_csv(L).iloc[:,1:]
                nametag = L.split('-')[-1].split('.')[0].lower()
                val[str(MAXCOLS)] = tags[nametag]
                print(f'name {L} used tag {tags[nametag]} as per key'\
                                         f' {nametag}')
                big_val = pd.concat([big_val,val],axis=0)
        except Exception as ins:
            print(ins.args)
            print(f'\n\n{L} failed\n')
    if not optional_flag:
        # train-val
        big_train.to_csv('total-train.csv')
        big_val.to_csv('val.csv')
        with open('tags.dat','w') as f:
            for I,K in tags.items():
                f.write(f'KEY: {K}    ITEM: {I}\n')
    else: 
        big_val.to_csv('test.csv')
        #for x in source:
        #    os.system(f'rm {x}')
    return

if __name__=='__main__':
    print('code: 0 is build train-val and 1 is build test\n\t--\t--\t--')
    MAXCOLS = int(sys.argv[2])
    print('ARGVAL CALL IS',sys.argv[1])
    building_call(bool(int(sys.argv[1])),MAXCOLS)
