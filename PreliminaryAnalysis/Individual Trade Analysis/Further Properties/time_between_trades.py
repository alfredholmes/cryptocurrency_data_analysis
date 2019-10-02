import ijson
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import expon
from scipy.stats import gaussian_kde

def main():
	with open('BTCUSDT.json', 'r') as f:
		trades = ijson.items(f, 'item')

		previous_price = None
		previous_time = None

		interarrivals = []
		changes = []


		for i, trade in enumerate(trades):
			#if previous_price is not None and int(trade['time']) - previous_time > 2000:
			if previous_price is not None:
				interarrival = int(trade['time']) - previous_time				
				interarrivals.append(interarrival)
				changes.append(float(trade['price']) - previous_price)
			if i > 10000:
				break

			previous_price = float(trade['price'])
			previous_time = int(trade['time'])

		to_remove = []


		for i, dt in enumerate(interarrivals):
			if dt < 50:
				to_remove.append(i)

		for index in reversed(to_remove):
			interarrivals.pop(index)

		plt.hist(interarrivals, 100, density=True, range=(0, 6000))

		loc, scale = expon.fit(interarrivals)
		x = np.linspace(0, 6000, 100)
		plt.plot(x, expon.pdf(x, scale=scale))


		

		plt.show()


if __name__ == '__main__':
	main()