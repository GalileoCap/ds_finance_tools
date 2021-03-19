#INFO: All configuration goes here, imported by other modules

import os

Data_dir = os.getenv('DATA_DIR', 'o_data') #U: Where to save and read downloaded data
def get_data_dir(): #U: Where to save and read downloaded data, ensure exists
	os.makedirs(Data_dir, exist_ok = True)
	return Data_dir

Tickers = ['AAPL', 'AMZN', 'GOOGL', 'KO', 'DISN', 'MELI', 'GOLD', 'XOM'] #U: Tickers we're interested in

Ratios = {'AAPL': 10, 'AMZN': 144, 'GOLD': 1, 'GOOGL': 58, 'KO': 5, 'MELI': 60, 'XOM': 5, 'DISN': 4} #U: BYMA CEDEAR to US stock ratio

Crypto = ['USDT', 'BTC', 'ETH'] #U: Cryptocoins we're insterested in

# S: Data source URLs ######################################
Spreadsheet_ID = 'Replace_with_the_id_of_your_spreadsheet_lGug' #U: ID of your Google sheet 

Cedear_url_base= 'https://www.rava.com/empresas/precioshistoricos.php?csv=1&e=CEDEAR' #U: Add ticker to the end

USDBlue_url_base= 'https://mercados.ambito.com/dolar/informal/historico-general/' #U: Base url to download dolar blue 

USDCCL_url = 'https://www.rava.com/empresas/precioshistoricos.php?e=DOLAR%20CCL&csv=1' #U: url for USD Contado Con Liqui

binance_p2p_url= 'https://p2p.binance.com/gateway-api/v2/public/c2c/adv/search' #U: To download Binance p2p prices

binance_p2p_rows_max= 20

# S: Google API ############################################
google_scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/gmail.compose'] #U: Scopes for access, in this case it's read/write for spreadsheets only

service_account_file = '.service.json' #U: Export your credentials from Google Console here

# S: Analysis ##############################################

MA_days = [7, 30, 100] #U: How many days to take into account for the moving averages

Fee = 0.01 #U: % per operation

Loss_max = 0.02 #U: Max % that we're willing to lose in a trade

Gain_min = 0.04 #U: Min % to go out winning in a trade

# S: Send report by mail ###################################

Mail_recipients = [] #U: List of email recipients' adresses

Mail_sender = None #U: Email sender adress

SMTP_login = (None, None) #U: Server (user, password) 

SMTP_host = (None, None) #U: SMTP (url, port)


