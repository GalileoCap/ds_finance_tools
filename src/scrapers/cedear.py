#INFO: download cedear prices from rava, may be used as main

import os
import sys
sys.path.insert(1, os.path.abspath(__file__+'/../../')) #A: Where you installed the library

from util.cfg import CFG, get_data_dir
from util.download_data import *

#**********************************************************************************************
#LIBRARY:

def cedear_url_name(ticker): #U: Generate rava url 
	if len(ticker) < 5:
		return CFG.Cedear_url_base+ticker
	else:
		return CFG.Cedear_url_base[0:4-len(ticker)]+ticker

def get_cedear(ticker): #U: Returns the updated data for this ticker's CEDEAR
	url = get_url(cedear_url_name(ticker), get_data_dir()+'/'+ticker+'_CEDEAR.csv')
	print('get_cedear_df', ticker, url)
	return url

#**********************************************************************************************
#EXAMPLE:

if __name__ == '__main__':
	for ticker in CFG.Tickers:
		get_cedear(ticker)
