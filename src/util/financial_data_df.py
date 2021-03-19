#INFO: Easy way to get DataFrames downloading data if necessary

from util.cfg import CFG, get_data_dir
from util.misc import *
from util.pandas import *
from scrapers.binance_p2p import get_binance_p2p_csv
from scrapers.cedear import *
from scrapers.stock import *

import pandas as pd
from dfply import *
from datetime import datetime
import os

def get_stock_df(ticker):
	df = pd.read_csv(get_stock(ticker))
	df.sort_values('Date', inplace = True) #A: Newest last
	return df

def get_cedear_df(ticker):
	df = pd.read_csv(get_cedear(ticker))
	df.sort_values('fecha', inplace = True)
	return df

def get_binance_p2p_df(ticker= 'USDT', buyOrSell= 'BUY', fiat= 'ARS'): #U: p2p offers in Binance, returns df
	df = pd.read_csv(get_binance_p2p_csv(ticker, buyOrSell, fiat))
	return df

def get_usdblue_df(): #U: Returns df with USDBlue prices
	anio_hoy = datetime.today().year
	fpath = get_data_dir() + f'/USD_BLUE_{anio_hoy}.csv'
	df = pd.read_csv(fpath, sep = '\t', header = 0, index_col = None)
	df.sort_values('fecha', inplace = True)
	df.set_index('fecha', inplace = True)
	return df

def get_usdccl_df(): #U: Returns df with USDCCL prices
	fpath = get_data_dir() + '/USD_CCL.csv'
	tmp_df = pd.read_csv(fpath, sep = ',', header = 0, index_col = None)
	df = tmp_df >> select(X.fecha, X.cierre) >> rename(usd_ccl = X.cierre) #U: Simple version
	df.sort_values('fecha', inplace = True)
	df.set_index('fecha', inplace = True)
	return df

def get_cedears_df(): #U: Returns a dict of df for all CEDEARS
	dolar_ccl = get_usdccl_df()

	stocks = {}
	cedears = {}

	for ticker in CFG.Tickers:
		df_usa = get_stock_df(ticker)
		if df_usa.columns[0] != 'Date':
			print(f'ERROR no data from USA for {ticker}')
			df_usa = None
		else:
			df_usa >>= mutate(fecha = X.Date)
			stocks[ticker] = df_usa
		#A: Read stock if it exists

		df = get_cedear_df(ticker)

		df >>= left_join(get_usdccl_df(), by = 'fecha', suffixes = ['', 'ccl']) #A: Added usd_ccl to each date

		ratio = CFG.Ratios[ticker]
		if ratio is None:
			print(f'ERROR there\'s no RATIO for {ticker}, assuming 1')
			ratio = 1

		df >>= mutate(cierre_ccl = X.cierre * ratio / X.usd_ccl)

		if not (df_usa is None):
			df >>= left_join(df_usa, by = 'fecha')
		
		for days in CFG.MA_days: #A: Moving averages
			df[f'ma{days}_ccl'] = df['cierre_ccl'].rolling(days, min_periods = 1).mean()
			df[f'ma{days}_usa'] = df['Close'].rolling(days, min_periods = 1).mean()
			df[f'min{days}_ccl'] = df['cierre_ccl'].rolling(days, min_periods = 1).min()
			df[f'min{days}_usa'] = df['Close'].rolling(days, min_periods = 1).min()
			#A: Rolling returns the values for each window, I can apply a function for series

		df['cierre_pct'] = df['cierre'].pct_change()
		df['cierre_ccl_pct'] = df['cierre_ccl'].pct_change()
	 
		if not (df_usa is None):
			df['cierre_usa_pct'] = df['Close'].pct_change()
			df >>= mutate(cierre_ccl_usa = X.cierre_ccl / X['Close']) #TODO: Check dates are equal

		cedears[ticker]= df

	return cedears
