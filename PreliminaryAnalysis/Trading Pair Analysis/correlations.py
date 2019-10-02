import plot
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

import multiprocessing

def main():
	to_load = ['BTCUSDT', 'ETHBTC']
	with multiprocessing.Pool() as p:
		btc, eth = p.map(plot.load_hourly_data, to_load)

	

	btc_returns = plot.calculate_returns(btc)
	eth_returns = plot.calculate_returns(eth)

	#btc_volume = [x[1] for x in btc]
	eth_volume = [y[1] for y in eth]

	lag = [i for i in range(0, 24)]

	corrs = []

	for i in lag:
		if i == 0:
			corrs.append(pearsonr(btc_returns, btc_returns)[0])

		if i > 0:
			corrs.append(pearsonr(btc_returns[i:], btc_returns[:-i])[0])

		if i < 0:

			corrs.append(pearsonr(btc_returns[:i], btc_returns[-i:])[0])

	plt.bar(lag, corrs)

	plt.xlabel('Offset')
	plt.ylabel('Correlation')

	plt.savefig('BTC return autocorrelation')

	plt.show()


if __name__ == '__main__':
	main()