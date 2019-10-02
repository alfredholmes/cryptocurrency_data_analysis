import ijson
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import expon

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

		#get the scale parameter for exponential

		tail_start = 1000

		loc, scale = expon.fit([t - tail_start for t in interarrivals if t > tail_start])

		x = np.linspace(0, 10 * scale, 100)

		exponential_tail_density = 1 - expon.cdf(tail_start, loc=0, scale=scale)
		observed_tail_density = len([t - tail_start for t in interarrivals if t > tail_start]) / len(interarrivals)

		base_proportion = observed_tail_density / exponential_tail_density
		print(base_proportion)

		plt.figure()

		plt.hist(interarrivals, bins=100, density=True, range=(0, 6000))
		plt.plot(x, base_proportion * expon.pdf(x, loc=0, scale=scale))

		plt.savefig('Exponential tail fitting')

		plt.figure()

		hist, edges = np.histogram(interarrivals, 100, density=True, range=(0, tail_start))
		abnormal_trades = []
		
		for i, dbin in enumerate(hist):
			abnormal_trades.append(dbin * (edges[i + 1] - edges[i]) - (base_proportion * (expon.cdf(edges[i + 1], loc=0, scale=scale) - expon.cdf(edges[i], loc=0, scale=scale))))

		plt.hist(edges[:-1], edges, weights=abnormal_trades)
		plt.savefig('Reaction trades')
		plt.show()

if __name__ == '__main__':
	main()