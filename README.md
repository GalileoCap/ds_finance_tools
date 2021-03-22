# Finance Tools

Convenient scripts to scrap and analyse financial data  
You can see it at work without installing on [Google Colab](https://colab.research.google.com/drive/18YDibEYh_BRFnh7qbnJ8JxdwVPa2sUc_?usp=sharing)

## Installing
~~~
#It's recommended that you create a virtual environment first
python3 -m venv finances
cd finances
source bin/activate
#If you don't want to use a virtual environment, you can skip to this step
git clone https://github.com/GalileoCap/ds_finance_tools.git
cd ds_finance_tools
pip install -r requirements.txt
~~~

## Analysis
In the file `src/app/demo/analysis/run_analyze_positions.py` you can see an example of how this scripts can be used to keep a tab on your positions and get trade recommendations as an email

## Scrapers
They can all be used as main
* binance_p2p: Downloads the current offers to buy crypto in BinanceP2P
* stock: Downloads the daily info of the configured tickers' US stocks from Stooq
* cedear: Downloads the daily info of the configured tickers' CEDEARs from Rava
*	usd: Downloads the daily info for the conversion rate of USD to ARS  

In the file `.env.json` you can specify the tickers and crypto you want to download and analyze  
The file `run_scrapers.py` dowloads and keeps up to date the data, you can schedule a cron service to run it every morning:
~~~
0 7 * * * python3 run_scrapers.py
~~~

## Connectors
They can both be used on their own

### mail_smtp
Used to send emails through an SMTP server.  
You need to configure the SMTP info, the sender address, and the receiving addresses in `.env.json`

### sheets_google
Used to read and update spreadhseets on Google Sheets.  
To set up:
* Create a an app on the [Google Cloud Platform](https://console.cloud.google.com/)
* Under "APIs & Services" go to "Credentials" and create a service account with owner access
* Then go to the new service account and add a new json key to it
* Download the json and save it as `.service.json` on the path from where you'll be running the scripts
