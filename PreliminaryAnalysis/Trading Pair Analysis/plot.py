import csv
import multiprocessing

import matplotlib.pyplot as plt

import datetime

import numpy as np

def load_hourly_data(symbol):
	#todo, remove hardcoding of times

	end = int(datetime.datetime.timestamp(datetime.datetime(2019, 6, 1))) * 1000
	hours = 365 * 24

	print('Getting Trades')

	#trades = binance.get_trades(symbol, end, hours)
	

	start = end - hours * 60 * 60 * 1000
	previous = start

	hourly_data = []
	volume = 0
	price_by_volume = 0

	print('Loading data...')

	i = 0

	with open('../Binance/' + symbol + '.csv', 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		volume = 0
		weighted_price = 0
		for line in reader:
			if int(line['Timestamp']) < previous:

				continue
			if int(line['Timestamp']) >= previous + 1000 * 60 * 60:
				if i % 100 == 0:
					print(symbol + ': ' + str(i) + '/' + str(hours))
				hourly_data.append([weighted_price / volume, volume])

				weighted_price = 0
				volume = 0
				i += int((int(line['Timestamp']) - previous) / (1000 * 60 * 60))
				if int((int(line['Timestamp']) - previous) / (1000 * 60 * 60)) > 1:
					hourly_data += [[0, 0]] * (i - 1)
				previous += (1000 * 60 * 60) * int((int(line['Timestamp']) - previous) / (1000 * 60 * 60))

			weighted_price += float(line['Price']) * float(line['Volume'])
			volume += float(line['Volume'])

	return hourly_data

def calculate_returns(hourly_data):
	previous = hourly_data[0][0]
	returns = []
	for hour in hourly_data:
		if hour[0] == 0:
			returns.append(1)

		else:
			returns.append(previous / hour[0])
			previous = hour[0]

	return returns


def main():
	to_load = ['BTCUSDT', 'ETHBTC']
	with multiprocessing.Pool() as p:
		btc, eth = p.map(load_hourly_data, to_load)
		
	btc_returns = calculate_returns(btc)
	eth_returns = calculate_returns(eth)

	plt.scatter(btc_returns, eth_returns, alpha = 0.05)


	plt.xlabel('BTC Price (USDT)')
	plt.ylabel('ETH Price (BTC)')

	plt.savefig('BTCUSDT, ETHBTC returns')

	plt.show()


if __name__ == '__main__':
	main()