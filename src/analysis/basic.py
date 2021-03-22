#INFO: Analyzes the moving averages of your positions

import os
import sys
sys.path.insert(1, os.path.abspath(__file__+'/../../')) #A: Where you installed the library

from util.cfg import CFG
from util._pandas import *
from util.misc import *
import pandas as pd

#******************************************
#MOVING AVERAGES

#U: Compara las medias de distinto rango, 
#OjO! de USA pq de Arg tenemos dificultad con el cambio de ratio en 2020
def check_averages(ticker):
	cedears = CFG.Cedears 

	ma100 = cedears[ticker]['ma100_usa'].iloc[-1]
	ma30 = cedears[ticker]['ma30_usa'].iloc[-1]
	ma7 = cedears[ticker]['ma7_usa'].iloc[-1]
	
	min100 = cedears[ticker]['min100_usa'].iloc[-1]
	min30 = cedears[ticker]['min30_usa'].iloc[-1]
	min7 = cedears[ticker]['min7_usa'].iloc[-1]
	
	precio = cedears[ticker]['Close'].iloc[-1] 
	#A: todo en dolares ccl!

	predigo= 'No se'
	porque= ''
	#TODO: Mejor forma de revisar, ¿que queremos ver? ¿Como lo hariamos?
	if ma7 < ma30 and ma7 < ma100: #A: Esta semana esta baja, pero predecimos que va a subir
		predigo = 'Sube'
		porque = 'ma7 < ma30 y ma100'
	elif ma30 < ma7 and ma7 < ma100: #A: Esta subiendo y va a seguir hacia la ma100
		predigo = 'Sube'
		porque = 'ma7 < ma100 PERO ma30 < ma7'
	elif ma100 < ma7 and ma7 < ma30: #A: Esta bajando para 'ajustarse' y va a seguir hacia la ma100
		predigo = 'Baja'
		porque = 'ma7 > ma100 AUNQUE ma7 < ma30'
	elif ma30 < ma7 and ma100 < ma7: #A: Esta subiendo, pero predecimos que va a bajar
		predigo = 'Baja'
		porque = 'ma7 > ma100 PERO ma30 < ma7'
	
	#TODO: Si no nos parece obvio a donde se va a mover, ¿nos quedamos?
	return (
		ticker, predigo, porque, precio, 
		(ma7 - precio) / precio, (ma30 - precio) / precio, (ma100 - precio) / precio,
		(min7 - precio) / precio, (min30 - precio) / precio, (min100 - precio) / precio
	)

def pred_medias(): #U: para todas las de la lista
	return df_from_lol(
		[['ticker','pred','razon','cierre','ma7dpct','ma30dpct','ma100dpct','min7dpct','min30dpct','min100dpct']] + [[
				ticker,
				pred,
				porque,
				precio,
				ma7pct,
				ma30pct,
				ma100pct,
				min7dpct,
				min30pct,
				min100pct
			]
			for ticker, pred, porque, precio, ma7pct, ma30pct, ma100pct, min7dpct, min30pct, min100pct in [
					check_averages(ticker) for ticker in CFG.Tickers
				]
			]
	)

#******************************************
#CHECKING OWNED STOCK

def process_position(row): #U: Converts the data from strings into floats 
  row['VarCant'] = float(row['VarCant'])
  row['VarARS'] = float(row['VarARS'])

  usdccl_price = float(CFG.usdccl.loc[row['Fecha']]['usd_ccl'])
  row['VarUSDCCL'] = row['VarARS'] / usdccl_price #U: Price for the USDCCL's at purchase date

  return row 

#U: Avisa si hay que vender una tenencia
def check_cedear(row):
	ticker = row['Ticker']
	df = CFG.Cedears[ticker]
	usdccl = CFG.usdccl['usd_ccl'].iloc[-1]

	cant = row['VarCant']
	ars = row['VarARS']
	ccl = row['VarUSDCCL']
	
	row['cierre'] = df['cierre'].iloc[-1] #TODO: Asegurarse que la fecha no sea demasiado vieja 
	row['cierre_ccl'] = row['cierre'] / df['usd_ccl'].iloc[-1]

	row['arsx1'] = ars / cant
	row['cclx1'] = ccl / cant

	new_ars = row['cierre'] * cant
	row['dif_ars'] = new_ars - ars
	row['dif_ars_pct'] = row['dif_ars'] / ars

	new_ccl = row['cierre_ccl'] * cant
	row['dif_ccl'] = new_ccl - ccl
	row['dif_ccl_pct'] = row['dif_ccl'] / ccl

	if row['dif_ccl_pct'] >= CFG.Loss_max: #A: Si ya estoy ganando lo ideal
		row['gano_pierdo'] = 'gana'
	elif row['dif_ccl_pct'] <= -CFG.Gain_min: #A: Si estoy perdiendo mas de lo aceptable
		row['gano_pierdo'] = 'PIERDO'
	else:
		row['gano_pierdo'] = 'Zafa'

	averages = check_averages(ticker)
	row['pred'] = averages[1] #A: Change predicted by the averages
	row['ma100dpct'] = averages[6] #A: Distance in pct from the 100 day average
	row['min100dpct'] = averages[9] #A: Distance in pct from the minimum in the past 100 days

	row['pierdo1pct'] = ccl / cant * df['usd_ccl'].iloc[-1] #A: In ar$
	row['pierdo0pct'] = row['pierdo1pct'] * 1.01 #A: Descontando el 1% de comision TODO: POner comision en config
	row['gano2pct'] = row['pierdo1pct'] * 1.03
	row['gano4pct'] = row['pierdo1pct'] * 1.05

	return row
	#TODO: Rango de precios para comprar y vender (ej. hasta qué precio puedo comprar o vender)
	#			 Ej. Si la media está un 5% arriba, hasta un 1% más caro puedo comprar y me guardo un margen de 4% para que suba, y al revés acepto perder hasta un 2% de lo que pagué en dolares
	#MEJOR: Lista de precios stop_loss piso, pierdo 2%, salgo hecho, gano 4%, gano 6%, gano mas

def check_binance(row): #U: Checks how much money we'd make with the lowest offers 
	ticker = row['Ticker']
	cant = row['VarCant']
	ars = row['VarARS']
	ccl = row['VarUSDCCL']

	usdccl = CFG.usdccl['usd_ccl'].iloc[-1]

	df = get_binance_p2p_df(ticker, 'SELL')
	tmp_cant = cant
	new_ars = 0
	for _, offer in df.iterrows():
		if 'Brubank' in offer['howToPay'] and float(offer['cantMin']) < tmp_cant: #A: I have enough for this offer
			#TODO: Check if it's a trustable buyer
			amt = min(tmp_cant, float(offer['cantMax'])) #A: Clamped to an amount I can sell

			new_ars += amt * float(offer['price'])
			tmp_cant -= amt

	new_ccl = new_ars / usdccl #A: To USDCCL

	row['dif_ars'] = new_ars - ars
	row['dif_ars_pct'] = row['dif_ars'] / ars

	row['dif_ccl'] = new_ccl - ccl
	row['dif_ccl_pct'] = row['dif_ccl'] / ccl

	if row['dif_ccl_pct'] >= CFG.Max_loss: #A: Si ya estoy ganando lo ideal
		row['gano_pierdo'] = 'gana'
	elif row['dif_ccl_pct'] <= -CFG.Min_gain: #A: Si estoy perdiendo mas de lo aceptable
		row['gano_pierdo'] = 'PIERDO'
	else:
		row['gano_pierdo'] = 'Zafa'

	row['pierdo1pct'] = ccl / cant * usdccl #A: In ar$
	row['pierdo0pct'] = row['pierdo1pct'] * 1.01
	row['gano2pct'] = row['pierdo1pct'] * 1.03
	row['gano4pct'] = row['pierdo1pct'] * 1.05

	row['pred'] = 'No se' #TODO: Predictions

	#TODO: Check averages 

	return row

def check_position(row):
	ticker = row['Ticker']
	if ticker in CFG.Tickers:
		#A: It's a CEDEAR
		return check_cedear(row)
	#elif ticker in CFG.Crypto:
	#	return check_binance(row)
	else:
		return row

ticker_actual = ''
saldo = 0
def calc_saldo(row):
	global ticker_actual, saldo
	if ticker_actual != row['Ticker']:
		ticker_actual = row['Ticker']
		saldo = row['VarCant']
	else:
		saldo += row['VarCant']
	row['SaldoCant'] = saldo

	return row

def texto_mail(row):
	ccl_hoy = CFG.usdccl['usd_ccl'].iloc[-1]

	ticker = row['Ticker']
	saldoCant = row['SaldoCant']
	gano_pierdo = row['gano_pierdo']
	pred = row['pred']
	dif_ars = float(row['dif_ars'])
	dif_ccl = float(row['dif_ccl'])
	cierre = float(row['cierre'])
	cierre_ccl = float(row['cierre_ccl'])
	compre_cclx1 = float(row['cclx1'])
	compre_cclx1_ars = compre_cclx1 * ccl_hoy
	stopLoss = row['StopLoss']
	ma100dpct = float(row['ma100dpct'])
	min100dpct = float(row['min100dpct'])
	text = f'''
{ticker} {gano_pierdo} {pred} {saldoCant:.0f} ar${dif_ars:.2f} ccl{dif_ccl:.2f}
stoploss ar${stopLoss} min100 ar${cierre * (1 + min100dpct):.2f} cierre ar${cierre:.2f} ccl{cierre_ccl:.2f}
ar$ -2%={compre_cclx1_ars * 0.99:.2f} 0%={compre_cclx1_ars * 1.01:.2f} +2%={compre_cclx1_ars * 1.03:.2f} +4%={compre_cclx1_ars * 1.05:.2f}
media100d% {ma100dpct:.2f} min100d% {min100dpct:.2f}
'''

	CFG.Report += text
	#print(text)

#U: Checks the state of each of our owned stocks
def report_positions():
	positions = CFG.Positions.apply(check_position, axis = 1)

	#print('TENENCIAS\n', positions.head(20))
	#print(position.iloc[0])

	positions_compra = positions[positions['VarARS'] > 0]
	positions_venta = positions[positions['VarARS'] < 0]

	positions_p_fifo = pd.concat([positions_venta, positions_compra]).sort_values('Ticker')
	#print('TENENCIAS_P_FIFO\n', positions_p_fifo.head(20))

	global ticker_actual, saldo; ticker_actual = ''; saldo = 0 #A: Reset values
	positions_actual = positions_p_fifo.apply(calc_saldo, axis = 1)

	#print('TENENCIAS_ACTUAL\n', positions_actual[['Ticker', 'VarCant', 'SaldoCant']].head(20),)

	con_saldo = positions_actual[positions_actual['SaldoCant'] > 0].apply(check_position, axis = 1)

	#print('CON_SALDO\n', con_saldo.head(20))
	#print(con_saldo.iloc[0])

	CFG.Report += '\n\nTENENCIAS:'
	con_saldo.apply(texto_mail, axis = 1)

def text_averages(row):
	usdccl = CFG.usdccl['usd_ccl'].iloc[-1]

	ticker = row.name
	pred = row['pred']
	ma100dpct = row['ma100dpct']
	min100dpct = row['min100dpct']
	ma30dpct = row['ma30dpct']
	min30dpct = row['min30dpct']
	ma7dpct = row['ma7dpct']
	min7dpct = row['min7dpct']
	cierre = row['cierre']
	cierre_ccl = cierre / usdccl
	text = f'''
{ticker} {pred} media100d% {ma100dpct:.2f} min100d% {min100dpct:.2f} media30d% {ma30dpct:.2f} min30d% {min30dpct:.2f} media7d% {ma7dpct:.2f} min7d% {min7dpct:.2f}
cierre ar${cierre:.2f} cierre ccl{cierre_ccl:.2f}, ar$ -2%={cierre * 0.96:.2f} +2%={cierre * 1.04:.2f}
'''

	CFG.Report += text
	#print(text)

def report_averages():
	df = pred_medias()
	df_check = df[df['ma100dpct'] > 0].sort_values('ma100dpct', ascending = False)
	#print(df_check.iloc[0])

	CFG.Report += '\n\nMEDIAS'
	df_check.apply(text_averages, axis = 1)
	#TODO: Viene subiendo, o viene bajando
	#TODO: Va a rebotar
	#TODO: Pisos y techos
	#TODO: Diferencia entre la media y precio
	#TODO: Cuando entrar a BTC
#Queremos:
#	Stop-loss que tenemos puesto
#	Cuántos papeles compramos a qé precio
#	Precio promedio ponderado, TODO: Para este hay que mezclar, ¿o como hacemos sino?
#	Precio que puedo vender (ya descontada la comisión, 0% = pierdo 0), -2% ccl, pierdo 0% ccl, 2% ccl
#	Si voy ganando, perdiendo, zafa
#	Distancia con las medias y minimos en %
# Agregar qué comprar (ordenadas por ma100dpct y que sea > 0):
#		Ticker, ma100dpct, min100dpc, ma30dpct, min30dpct, ma7dpct, min7dpct, min100 ar$, cierre ars$, cierre ccl, -2%=cierre * 0.96, +2%=cierre * 1.04

