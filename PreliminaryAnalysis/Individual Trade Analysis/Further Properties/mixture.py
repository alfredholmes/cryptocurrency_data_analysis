from sklearn.mixture import GaussianMixture as gm

import ijson
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


		mixture_model = gm(n_components=2)
		labeled_changes = mixture_model.fit_predict(np.array(changes).reshape(-1, 1))
		print(labeled_changes)

		plt.figure()
		d = [change for i, change in enumerate(changes) if labeled_changes[i] == 0]
		plt.hist([change for i, change in enumerate(changes) if labeled_changes[i] == 0], 100, density=True)

		loc, scale = norm.fit(d)
		x = np.linspace(loc - 4 * scale, loc + 4 * scale, 100)
		plt.plot(x, norm.pdf(x, loc=loc, scale=scale))

		#plt.hist([change for i, change in enumerate(changes) if labeled_changes[i] == 1], 100, density=True, alpha=0.5)

		plt.savefig('Gaussian fit of thinned data')

		plt.show()




if __name__ == '__main__':
	main()