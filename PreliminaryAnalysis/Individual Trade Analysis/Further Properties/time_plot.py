import ijson
import numpy as np
import matplotlib.pyplot as plt


def main():
	with open('BTCUSDT.json', 'r') as f:
		trades = ijson.items(f, 'item')

		previous_price = None
		previous_time = None

		interarrivals = []
		changes = []


		for i, trade in enumerate(trades):
			if i > 1000:
				break
			#if previous_price is not None and int(trade['time']) - previous_time > 2000:
			if previous_price is not None:
				interarrival = int(trade['time']) - previous_time				
				interarrivals.append(interarrival)
				changes.append(float(trade['price']) - previous_price)


			previous_price = float(trade['price'])
			previous_time = int(trade['time'])

		plt.scatter(np.cumsum(interarrivals), [1 for x in interarrivals], alpha=0.5)
		plt.plot(np.cumsum(interarrivals), np.cumsum(changes))

		plt.show()

if __name__ == '__main__':
	main()