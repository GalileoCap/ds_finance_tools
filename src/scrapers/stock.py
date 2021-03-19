from util.cfg import CFG, get_data_dir
from util.misc import *
import pandas_datareader.data as web

#**********************************************************************************************
#LIBRARY:

def get_stock(ticker): #U: Returns the updated data for this ticker from USA 
	ticker = 'DIS.US' if ticker == 'DISN' else ticker #A: See https://stooq.com/q/a2/?s=dis.us

	print(f'get_stock_usa {ticker}')
	path = get_data_dir()+'/'+ticker+'_USD_stooq.csv'

	if not isFromToday_file(path):
		#A: We have to update the file
		f = web.DataReader(ticker, 'stooq')
		f.to_csv(path)

	return path

#**********************************************************************************************
#EXAMPLE:

if __name__ == '__main__':
	tickers = ['AAPL', 'AMZN', 'GOOGL', 'KO', 'DISN', 'GOLD', 'XOM']

	for ticker in tickers:
		get_stock(ticker)
