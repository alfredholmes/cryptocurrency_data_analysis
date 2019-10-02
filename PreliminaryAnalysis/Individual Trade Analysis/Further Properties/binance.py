import requests
import json
import csv

import datetime

import multiprocessing

import time

import matplotlib.pyplot as plt
from scipy.stats import expon

import numpy as np


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
	api = Binance('Rgq1YpCutNL6HbCbxYwnJtq041Bh1ndUSrufCHAOZ0xOkpgyPYjFHDfmI5FbECq5')

	last_id = 0
	last_timestamp = end_timestamp

	if end_timestamp is None:
		#get most recent trades
		last_trade = json.loads(api.get('/api/v1/trades', {'symbol': symbol, 'limit': 1}).text)

		last_id = int(last_trade[0]['id'])
		last_timestamp = int(last_trade[0]['time'])
	else:
		trades = json.loads(api.get('api/v1/aggTrades', {'symbol': symbol, 'startTime': int(last_timestamp - 1000 * 60 * 60 * 0.1), 'endTime': int(last_timestamp), 'limit': 1}).text)
		print(trades)
		last_id = trades[-1]['l']


	trade_time = last_timestamp


	min_time_per_request = 0.5 #api call has weight of 5

	data = []

	while trade_time > last_timestamp - hours * 60 * 60 * 1000:
		request_sent = time.time()
		r = api.get('api/v1/historicalTrades', {'symbol': symbol, 'limit': 1000, 'fromId': last_id - 1000})

		trades = json.loads(r.text)

		trades.extend(data)

		data = trades

		last_id = int(trades[0]['id'])
		trade_time = int(trades[0]['time'])



		#prevent spamming the api
		if time.time() - request_sent < min_time_per_request:
			time.sleep(min_time_per_request - (time.time() - request_sent))


	return data








def main():
	symbol = 'BTCUSDT'
	#symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'ETHBTC', 'LTCBTC', 'LTCETH']
	#symbols = ['ETHUSDT', 'LTCUSDT', 'ETHBTC', 'LTCBTC', 'LTCETH']

	#trades = get_trades('BTCUSDT', datetime.datetime.timestamp(datetime.datetime(2019, 6, 1)) * 1000, 24 * 365)
	trades = get_trades(symbol, datetime.datetime.timestamp(datetime.datetime(2019, 6, 1)) * 1000, 1200)


	with open(symbol + '.json', 'w') as f:
		json.dump(trades, f)

	previous_time = None

	interarrival_times = []

	for trade in trades:
		time = trade['time']

		if previous_time is not None:
			interarrival_times.append(time - previous_time)

		previous_time = time

	plt.hist(interarrival_times, 100, density=True)
	loc, scale = expon.fit(interarrival_times, loc=0)
	x = np.linspace(0, 2000, 100)
	plt.plot(x, expon.pdf(x, loc=loc, scale=scale))
	plt.show()



if __name__ == '__main__':
	main()
