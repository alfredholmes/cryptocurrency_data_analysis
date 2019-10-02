import ijson
import pandas

import numpy as np


from scipy.stats import norm, expon

import matplotlib.pyplot as plt

def main():
	with open('BTCUSDT.json', 'r') as f:
		trades = ijson.items(f, 'item')

		previous_price = None
		previous_time = None
		changes = []
		interarrivals = []
		volumes = []

		for trade in trades:
			#if previous_price is not None and int(trade['time']) - previous_time > 2000:
			if previous_price is not None:
			
				price_change = float(trade['price']) - float(previous_price)
				changes.append(price_change)
				interarrivals.append(int(trade['time']) - previous_time)
				volumes.append(float(trade['qty']))
			previous_price = float(trade['price'])
			previous_time = int(trade['time'])
			if len(changes) > 10000:
				break
	
	plt.figure('Price Movements')

	plt.hist(changes, 100, density=True)

	loc, scale = norm.fit(changes)
	x = np.linspace(loc - 4 * scale, loc + 4 * scale, 100)


	plt.plot(x, norm.pdf(x, loc=loc, scale=scale))

	plt.savefig('BTCUSDT Trade Delta for low frequency trades')

	plt.figure('Interarrivals')

	loc, scale = expon.fit(interarrivals)
	#interarrivals = [t for t in interarrivals if t < loc + 10 * scale]
	plt.hist(interarrivals, 100, density=True, range=(0, loc + 10000))

	x = np.linspace(loc, loc + 10000, 100)
	plt.plot(x, expon.pdf(x, loc=loc, scale=scale), label='Exponential, r=' + str(1 / scale))

	plt.legend()


	plt.xlabel('Time')
	plt.ylabel('Density')

	plt.savefig('BTCUSDT Exponential tail')

	plt.figure('Delta S against Delta T')

	#plt.scatter(interarrivals, changes, alpha=0.01)

	plt.scatter(changes[:-1], interarrivals[1:], alpha=0.1)
	

	plt.figure()
	plt.scatter(volumes, changes=0.01)


	plt.show()




if __name__ == '__main__':
	main()