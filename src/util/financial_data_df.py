#INFO: Easy way to get DataFrames downloading data if necessary

import os
import sys
sys.path.insert(1, os.path.abspath(__file__+'/../../')) #A: Where you installed the library

from util.cfg import CFG, get_data_dir
from util.misc import *
from util._pandas import *
from scrapers.binance_p2p import get_binance_p2p_csv
from scrapers.cedear import *
from scrapers.stock import *
from scrapers.usd import *

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
	fpath = get_usd_blue() 
	df = pd.read_csv(fpath, sep = '\t', header = 0, index_col = None)
	df.sort_values('fecha', inplace = True)
	df.set_index('fecha', inplace = True)
	return df

def get_usdccl_df(): #U: Returns df with USDCCL prices
	fpath = get_usd_ccl() 
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
			df[f'max{days}_ccl'] = df['cierre_ccl'].rolling(days, max_periods = 1).max()
			df[f'max{days}_usa'] = df['Close'].rolling(days, max_periods = 1).max()
			#A: Rolling returns the values for each window, I can apply a function for series

			df[f'ma{days}_ccl_dpct'] = (df[f'ma{days}_ccl'] - df['cierre_ccl']) / df['cierre_ccl']
			df[f'min{days}_ccl_dpct'] = (df[f'min{days}_ccl'] - df['cierre_ccl']) / df['cierre_ccl']
			df[f'max{days}_ccl_dpct'] = (df[f'max{days}_ccl'] - df['cierre_ccl']) / df['cierre_ccl']
			df[f'ma{days}_usa_dpct'] = (df[f'ma{days}_usa'] - df['Close']) / df['Close']
			df[f'min{days}_usa_dpct'] = (df[f'min{days}_usa'] - df['Close']) / df['Close']
			df[f'max{days}_usa_dpct'] = (df[f'max{days}_usa'] - df['Close']) / df['Close']
			#A: Pct distance from the averages

		df['ema12_ccl'] = df['cierre_ccl'].ewm(span = 12, min_periods = 1).mean()
		df['ema26_ccl'] = df['cierre_ccl'].ewm(span = 26, min_periods = 1).mean()
		df['macd_ccl'] = df['ema12_ccl'] - df['ema26_ccl']
		df['ema12_usa'] = df['Close'].ewm(span = 12, min_periods = 1).mean()
		df['ema26_usa'] = df['Close'].ewm(span = 26, min_periods = 1).mean()
		df['macd_usa'] = df['ema12_usa'] - df['ema26_usa']

		df['cierre_pct'] = df['cierre'].pct_change()
		df['cierre_ccl_pct'] = df['cierre_ccl'].pct_change()
	 
		if not (df_usa is None):
			df['cierre_usa_pct'] = df['Close'].pct_change()
			df >>= mutate(cierre_ccl_usa = X.cierre_ccl / X['Close']) #TODO: Check dates are equal

		cedears[ticker]= df

	return cedears
