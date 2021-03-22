#INFO: Analyze positions and get an email with predictions

import os
import sys
sys.path.insert(1, os.path.abspath(__file__+'/../../../../')) #A: Where you installed the library

from util.cfg import CFG
from util.financial_data_df import *
from util.pandas import *
from util.misc import *
from connectors.sheets_google import *
from analysis.basic import *

from datetime import datetime

# S: Setup #################################################
init_sheets()

#CEDEARS

CFG.Cedears = get_cedears_df()

data = [['ticker', 'ratio', 'arsmkt', 'usamkt']] + ( #U: Data to update in the sheet
[
	[   
		ticker,
		CFG.Ratios[ticker],
		CFG.Cedears[ticker]['cierre'].iloc[-1],
		CFG.Cedears[ticker]['Close'].iloc[-1]
	]   
	for ticker in CFG.Tickers
])  
set_to_sheet(CFG.Spreadsheet_ID, 'Cotizaciones', data) #A: Sheet's updated

#Dollar
CFG.usdccl = get_usdccl_df()
CFG.usdblue = get_usdblue_df()

sheet_usdblue = CFG.usdblue.sort_index(ascending = False) #A: Latest first
set_df_to_sheet(CFG.Spreadsheet_ID, 'USD', sheet_usdblue)

#Positions
CFG.Positions = get_df_from_sheet(CFG.Spreadsheet_ID, 'Tenencias', idx_col = None)
CFG.Positions = CFG.Positions.apply(process_position, axis = 1)

#Crypto
#CFG.usdt_p2p_ars_sell = get_binance_p2p_df(ticker = 'USDT', buyOrSell = 'SELL')
#CFG.btc_p2p_ars_sell = get_binance_p2p_df(ticker = 'BTC', buyOrSell = 'SELL')
#CFG.eth_p2p_ars_sell = get_binance_p2p_df(ticker = 'ETH', buyOrSell = 'SELL')

#CFG.usdt_p2p_ars_buy = get_binance_p2p_df(ticker = 'USDT')
#CFG.btc_p2p_ars_buy = get_binance_p2p_df(ticker = 'BTC')
#CFG.eth_p2p_ars_buy = get_binance_p2p_df(ticker = 'ETH')

# S: Analysis #############################################
#Recommended trades
pred_medias_df = pred_medias()

#Report
CFG.Report = f'Report for {datetime.now().strftime("%Y-%m-%d")}'
CFG.Report += f'\n\nUSDCCL {CFG.usdccl.iloc[-1]["usd_ccl"]}'

report_positions()
report_averages()

print(CFG.Report)
#send_emails(Report)
