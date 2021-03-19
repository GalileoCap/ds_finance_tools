#INFO: Generic functions for downloading

from util import cfg #U: Common settings for our modules
from util.misc import *
import os
import requests
import shutil

def get_url_now(url, fpath): #U: Downloads from the url and saves it to fpath 
	with requests.get(url, stream=True) as r:
		with open(fpath, 'wb') as f:
			shutil.copyfileobj(r.raw, f)

	return fpath

def get_url(url, fpath): #U: Updates the file with the data from the url if older than one day
	if not isFromToday_file(fpath): #A: We have to update the file
		print(f'get_url {fpath} downloading')
		get_url_now(url, fpath)

	return fpath

if __name__ == '__main__':
	url = 'https://www.rava.com/empresas/precioshistoricos.php?e=DOLAR%20CCL&csv=1' #U: Url to the csv

	get_url(url, cfg.get_data_dir()+'/USD_MEP.csv')
