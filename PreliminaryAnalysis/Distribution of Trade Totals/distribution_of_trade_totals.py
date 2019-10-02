import csv
import datetime

import matplotlib.pyplot as plt

import numpy as np
from scipy.misc import factorial
from scipy.stats import norm, skewnorm, exponnorm

def poisson_density(x, mu):
	#return np.exp(-mu) * x / factorial(x)
	return 1 / np.sqrt(2 * np.pi * x) * np.exp(x * (1 - mu - x * np.log(mu) - np.log(x)))
def main():
	symbol = 'BTCUSDT'
	start = int(datetime.datetime.timestamp(datetime.datetime(2019, 6, 1))) * 1000 - 365 * 24 * 60 * 60 * 1000
	previous = start
	trades = []
	total_trades = 0
	max_trades = 0
	time_step = 1
	with open('../Binance/' + symbol + '.csv', 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for line in reader:
			if int(line['Timestamp']) > previous + time_step * 60 * 60 * 1000:
				previous += time_step * 60 * 60 * 1000
				trades.append(total_trades)
				if max_trades < total_trades:
					max_trades = total_trades
				total_trades = 0
			total_trades += 1

	mean = np.mean(trades)
	print(mean)

	trades = [t for t in trades if t != 1]

	#mean, scale = norm.fit(np.log(trades))
	a, loc, scale = skewnorm.fit(np.log(trades))
	loc_n, scale_n = norm.fit(np.log(trades))

	k, loc_ne, scale_ne = exponnorm.fit(np.log(trades))

	plt.hist(np.log(trades), bins=100, density=True)
	x = np.linspace(6, 12, 100)
	plt.plot(x, skewnorm.pdf(x, a, loc=loc, scale=scale), label='skewnorm')
	plt.plot(x, norm.pdf(x, loc=loc_n, scale=scale_n), label='norm')
	plt.plot(x, exponnorm.pdf(x, k, loc=loc_n, scale=scale_n), label='Exponentially modified Gaussian')

	plt.xlabel('Log Trades')
	plt.ylabel('Density')

	plt.legend()

	#plt.plot([i for i in range(1, max_trades)], poisson_density(np.array([i for i in range(1, max_trades)]), mean))
	#plt.plot([i for i in range(0, max_trades)], norm.pdf([i for i in range(max_trades)], loc=mean, scale=np.sqrt(mean)))
	plt.savefig(symbol + ' log Trades')

	plt.show()


if __name__ == '__main__':
	main()