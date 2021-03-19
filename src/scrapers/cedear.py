from util import cfg
from util.download_data import *

#**********************************************************************************************
#LIBRARY:

def cedear_url_name(ticker): #U: Generate rava url 
	if len(ticker) < 5:
		return cfg.Cedear_url_base+ticker
	else:
		return cfg.Cedear_url_base[0:4-len(ticker)]+ticker

def get_cedear(ticker): #U: Returns the updated data for this ticker's CEDEAR
	url = get_url(cedear_url_name(ticker), cfg.get_data_dir()+'/'+ticker+'_CEDEAR.csv')
	print('get_cedear_df', ticker, url)
	return url

#**********************************************************************************************
#EXAMPLE:

if __name__ == '__main__':
	for ticker in cfg.Tickers:
		get_cedear(ticker)
