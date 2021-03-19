#INFO: Download all data, e.g. from Cron

import sys
sys.path.insert(1, '../../') #A: Where you installed the library

from util import cfg
from scrapers.stock import *
from scrapers.cedear import *
from scrapers.usd import *
from scrapers.binance_p2p import *

def run_scrapers_all():
	for ticker in cfg.Tickers:
		get_stock(ticker)
		get_cedear(ticker)

	for ticker in cfg.Crypto:
		get_binance_p2p_csv(ticker, 'BUY')
		get_binance_p2p_csv(ticker, 'SELL')

	get_usd_blue()
	get_usd_ccl()

if __name__ == '__main__':
	run_scrapers_all()
