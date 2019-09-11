import requests
import json
import csv

import datetime

import multiprocessing

import os


class Binance:
	def __init__(self, api_key):
		self.api_key = api_key
		self.base = 'https://api.binance.com/'
		self.api_header = {'X-MBX-APIKEY': self.api_key}

	""" Endpoint is the binance api endpoint required and the parameters... 
	"""
	def get(self, endpoint, parameters):
		result = requests.get(self.base + endpoint, params = parameters, headers=self.api_header)
		return result

	def get_request_limit_info(self):
		result = self.get('/api/v1/exchangeInfo', None)
		return json.loads(result.text)
		# TODO: parse this 

def write_array_to_csv(file, headers, arr, append='True'):
	mode = 'w'
	if append:
		mode = 'a+'
	with open(file, mode) as csvfile:
		writer = csv.writer(csvfile)
		if not append or csvfile.tell() == 0:
			writer.writerow(headers)
		for line in arr:
			writer.writerow(line)

def get_trades(symbol, end_timestamp, hours):
	api = Binance('API KEY')
	if end_timestamp is None:
		end = int(datetime.datetime.timestamp(datetime.datetime(2018, 6, 1))) * 1000
	else:
		end = end_timestamp
	ms_per_hour = 60 * 60 * 1000


	data = []


	for i in range(hours):
		if i % 24 == 0:
			print('\t' + symbol + ': ' + str(int(i / 24)) + '/' + str(int(hours / 24)))
		r = api.get('/api/v1/aggTrades', {'symbol': symbol, 'startTime': str(end - ms_per_hour), 'endTime': str(end - 1)})

		if r.status_code != 200:
			print(r.text, r.headers)
			break
		trades = []
		
		for trade in json.loads(r.text):
			
			price = float(trade['p'])
			volume = float(trade['q'])
			time = int(trade['T'])
			maker = int(trade['m'])
			first_trade = int(trade['f'])
			last_trade = int(trade['l'])
			
			trades.append([price, volume, time, maker, first_trade, last_trade])
		trades.reverse()
		data += trades
		end = end - ms_per_hour
		
	data.reverse()
	return data

def main():
	
	#Change this array to download the data from different currencies
	#symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'ETHBTC', 'LTCBTC', 'LTCETH']
	symbols = ['BTCUSDT', 'ETHBTC']
	
	#the start times of the files that are to be downloaded 
	months = [datetime.datetime(2018, 4 + i, 1) for i in range(9)] + [datetime.datetime(2019, i + 1, 1) for i in range(7)]
	
	for i in range(len(months) - 1):

		print(months[i].strftime('%Y%m') + ':')

		start = int(datetime.datetime.timestamp(months[i])) * 1000
		end = int(datetime.datetime.timestamp(months[i + 1])) * 1000
		hours = int((end - start) / (1000 * 60 * 60)) 
		


		dir_str = months[i].strftime('%Y%m') + '/'

		try:
			os.mkdir(months[i].strftime('%Y%m'))
		except FileExistsError as e:
			pass

		for symbol in symbols:
			write_and_save_data(symbol, end, hours, dir_str)
			print()




	
def write_and_save_data(symbol, end, hours, dir_str = ''):
	trades = get_trades(symbol, end, hours)
	with open(dir_str + symbol + '.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		if csvfile.tell() == 0:
			writer.writerow(['price', 'volume', 'timestamp', 'maker', 'first_trade', 'last_trade'])
		for trade in trades:
			writer.writerow(trade)

	





if __name__ == '__main__':
	main()
