#INFO: download p2p prices from binance, may be used as main

import os
import sys
sys.path.insert(1, os.path.abspath(__file__+'/../../')) #A: Where you installed the library

from util.cfg import CFG, get_data_dir
import os
import shutil
import requests
import json
from datetime import datetime
import gzip

def get_binance_p2p_json(ticker= 'USDT', buyOrSell= 'BUY', fiat= 'ARS'): #U: p2p asking prices from Binance, returns json
	query= {"page":1,"rows": CFG.binance_p2p_rows_max,"payTypeList":[],"asset": ticker,"tradeType": buyOrSell,"fiat": fiat}
	r= requests.post(CFG.binance_p2p_url,  json= query)
	data= r.json()
	return data

def get_binance_p2p_lol(ticker= 'USDT', buyOrSell= 'BUY', fiat= 'ARS'): #U: p2p asking prices from Binance, returns LoL 
	d= get_binance_p2p_json(ticker, buyOrSell, fiat)
	data= [
		['price', 'qtyMin', 'qtyMax', 'howToPay', 'usrId', 'usrNick', 'usrOk30dPct', 'usrBuy30d', 'usrSell30d']
	 ] + [ 
		[
		oferta['advDetail']['price'],
		oferta['advDetail']['minOrderAmount'],
		oferta['advDetail']['dynamicMaxOrderAmount'],
		', '.join( list(map( lambda p: p['identifier'], oferta['advDetail']['payMethodDtos'] ))),
		oferta['merchant']['merchantNo'],
		oferta['merchant']['nickName'],
		oferta['merchant']['userStatsRet']['finishRateLatest30day'],
		oferta['merchant']['userStatsRet']['completedSellOrderNumOfLatest30day'],
		oferta['merchant']['userStatsRet']['completedBuyOrderNumOfLatest30day'],
		]
		for oferta in d['data']
	]
	return data

def get_binance_p2p_csv(ticker= 'USDT', buyOrSell= 'BUY', fiat= 'ARS'): #U: p2p asking prices from Binance, returns DataFrame
	data_lol= get_binance_p2p_lol(ticker, buyOrSell, fiat)
	os.makedirs(get_data_dir()+'/binance_p2p', exist_ok= True) #A: Create dir if it does not exist 
	fpath= get_data_dir()+'/binance_p2p/'+ticker+'_'+fiat+'_'+buyOrSell+'_'+datetime.now().strftime('%Y-%m-%d-%H')+'.csv' #A: Save at most one per hour
	with gzip.open(fpath+'.gz', "wt") as fout:
		fout.write('\n'.join([ '\t'.join(map(str,row)) for row in data_lol]) )
	
	return fpath

if __name__ == '__main__':
	for ticker in CFG.Crypto:
		get_binance_p2p_csv(ticker, 'BUY')
		get_binance_p2p_csv(ticker, 'SELL')
