import requests
import json
import csv

import datetime, time
import math

import os


class Binance:
	def __init__(self, api_key):
		self.api_key = api_key #not actually required for the implemented api calls, but may be required for other api requests
		self.base = 'https://api.binance.com/'
		self.api_header = {'X-MBX-APIKEY': self.api_key}

	""" Endpoint is the binance api endpoint required and the parameters are dependent on the
	"""
	def get(self, endpoint, parameters=''):
		result = requests.get(self.base + endpoint, params = parameters, headers=self.api_header)
		return result


	def get_request_limit(self):
		requests_per_minute = int(json.loads(self.get('/api/v1/exchangeInfo').text)['rateLimits'][0]['limit'])
		seconds_per_request = 1 / (requests_per_minute / 60)
		return seconds_per_request

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
		end = int(end_timestamp)

	ms_per_hour = 60 * 60 * 1000
	#get the rate limts to prevent 423 errors

	seconds_per_request = api.get_request_limit()


	data = []


	for i in range(hours):
		previous_time = time.time()
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
			timestamp = int(trade['T'])
			maker = int(trade['m'])
			first_trade = int(trade['f'])
			last_trade = int(trade['l'])

			trades.append([price, volume, timestamp, maker, first_trade, last_trade])
		trades.reverse()
		data += trades
		end = end - ms_per_hour

		if time.time() - previous_time < seconds_per_request:
			time.sleep(seconds_per_request - (time.time() - previous_time))

	data.reverse()
	return data

def main():

	#Change this array to download the data from different currencies
	#symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'ETHBTC', 'LTCBTC', 'LTCETH']
	symbols = ['BTCUSDT', 'ETHBTC']

	#the start times of the files that are to be downloaded
	start_year = 2018
	start_month = 4 #the month of the year (> 0)
	months = [i for i in range(15)] #get 15 months worth of data starting at 20180401

	for i in months:
		year = start_year + math.floor((start_month + i - 1) / 12)
		month = (start_month + i - 1) % 12 + 1

		next_year = start_year + math.floor((start_month + i) / 12)
		next_month = (start_month + i) % 12 + 1

		start = datetime.datetime(year, month, 1).timestamp() * 1000
		end = datetime.datetime(next_year, next_month, 1).timestamp() * 1000

		hours = int((end - start) / (1000 * 60 * 60))


		for symbol in symbols:
			write_and_save_data(symbol, year, month, end, hours)






def write_and_save_data(symbol, year, month, end, hours):
	trades = get_trades(symbol, end, hours)

	try:
		os.mkdir(str(year) + '/' + str(month))
	except FileExistsError:
		pass
	except FileNotFoundError:
		os.mkdir(str(year))
		os.mkdir(str(year) + '/' + str(month))

	dir_str = str(year) + '/' + str(month) + '/'

	with open(dir_str + symbol + '.csv', 'w') as csvfile:
		writer = csv.writer(csvfile)
		if csvfile.tell() == 0:
			writer.writerow(['price', 'volume', 'timestamp', 'maker', 'first_trade', 'last_trade'])
		for trade in trades:
			writer.writerow(trade)







if __name__ == '__main__':
	main()
