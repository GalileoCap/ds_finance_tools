from util.cfg import CFG, get_data_dir
from util.misc import *
from util.download_data import *
import requests
import json
from datetime import datetime

#**********************************************************************************************
#LIBRARY:

def set_file_csv_lol(fpath, lol): #U: Writes a list of lists as a csv 
	with open(fpath, 'w') as f:
		f.write( '\n'.join(['\t'.join(r) for r in lol]))

def usdblue_url(desde = None, hasta = None): #U: url to download json from Ambito 
	desde = datetime(2018, 1, 1) if desde is None else desde
	hasta = datetime.today() if hasta is None else hasta
	return CFG.USDBlue_url_base + desde.strftime('%d-%m-%Y') + '/' + hasta.strftime('%d-%m-%Y')

def get_usd_blue(anio_desde = 2018, anio_hasta = None): #U: Downloads usdblue prices and stores it as a csv 
	anio_hoy = datetime.today().year
	anio_hasta = anio_hoy if anio_hasta is None else anio_hasta 


	for anio in range(anio_desde, anio_hasta+1):
		fpath = f'{get_data_dir()}/USD_BLUE_{anio}.csv'
		url = None #A: Assigned only if we need to update with new data
		if anio < anio_hoy and get_file_mtime(fpath) == 0: #A: We skip over the years we already have 
			url = usdblue_url(datetime(anio, 1, 1),datetime(anio, 12, 31))
			print(f'get_usd_blue {anio} < {anio_hoy} no esta', fpath, url)
		elif not isFromToday_file(fpath): #A: We're updating this year 
			url = usdblue_url(datetime(anio, 1, 1)) #A: Since January 1st up until today 
			print(f'get_usd_blue el de hoy no esta', fpath, url)
		else:
			print(f'get_usd_blue estaba no hago nada', fpath)

		if not url is None: #A: We have to update
				req = requests.get(url)
				txt = req.text
				print(f'usdblue {anio} from {url} is {txt[0:20]}')
				lolx = json.loads(txt)
				data = [['fecha', 'compra', 'venta']]
				data += list(reversed([
								[
									f'{r[0][6:10]}{r[0][2:6]}{r[0][0:2]}',
									r[1].replace(',', '.'),
									r[1].replace(',', '.')
								]
								for r in lolx[1:]
							]))
				#A: Formatted for pandas 
				set_file_csv_lol(fpath, data) #A: Saving

def get_usd_ccl(): #U: Downloads USDCCL data
	get_url(CFG.USDCCL_url, get_data_dir() + '/USD_CCL.csv')

#**********************************************************************************************
#EXAMPLE:

if __name__ == '__main__':
	get_usd_blue()
	get_usd_ccl()
