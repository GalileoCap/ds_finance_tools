#INFO: General purpose functions

import re
import glob
import gzip
import json
import multiprocessing
import math
import os
import sys
from datetime import datetime
import string

LETTERS_AZ = list(string.ascii_lowercase)

APP_DIR = os.path.abspath(__file__+'/../../../') #A: The root folder for your app
CFG_out_dir = './o_data' #TODO: Configure
CFG_data_dir = './o_data'

def get_file_mtime(fpath): #U: Date of last change or 0 
	try:
		stat = os.stat(fpath)
		return stat.st_mtime
	except:
		return 0

def isFromToday_file(fpath): #U: True if the file is from today
	today = datetime.today().day
	file_day = datetime.fromtimestamp(get_file_mtime(fpath)).day
	return file_day == today

def read_file(fname, prefix_dir =CFG_data_dir, compressed= None):
	compressed= fname[-3:]=='.gz' if compressed==None and len(fname)>3 else compressed

	if compressed:
		with gzip.open(prefix_dir+'/'+fname,'r') as f:
			return f.read().decode('utf-8')
	else:
		with open(prefix_dir+'/'+fname,'rt') as f:
			return f.read()


def write_file(data,fname, prefix_dir=CFG_data_dir, compressed= None):
	compressed= path[-3:]=='.gz' if compressed==None and len(path)>3 else compressed

	if compressed:
		with gzip.open(prefix_dir+'/'+fname, 'w') as fout:
			fout.write(data.encode('utf-8'))
	else:
		with open(prefix_dir+'/'+fname, 'wt') as fout:
			fout.write(data)

def read_gzip(fname):
  with gzip.open(fname,'rt') as f:
    return f.read()

def write_json(data,fname):
  with gzip.open(CFG_out_dir+'/'+fname+'.json.gz', 'w') as fout:
    fout.write(json.dumps(data).encode('utf-8'))                       

def read_json(fname, prefix_dir=CFG_data_dir, compressed= None, ext= '.json.gz'):
	fname= fname+ext
	return json.loads( read_file(fname, prefix_dir, compressed) )

class AttrDict(dict): #U: To access X['Y'] as X.Y
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def set_env(k,v, overwrite= True):
	if overwrite or os.environ.get(k) is None:
		os.environ[k]= str(v) #A: python espera solo strings

def dict_to_env(aDict, overwrite= True):
	for k in aDict.keys():
		set_env(k, aDict[k], overwrite)

def json_to_env(fname= '.env', prefix_dir=APP_DIR, overwrite= True):
	d= read_json(fname, prefix_dir, False, '.json')
	dict_to_env(d, overwrite)
	return d

