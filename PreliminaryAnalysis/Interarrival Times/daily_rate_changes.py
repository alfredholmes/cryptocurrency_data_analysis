import classification

import numpy as np

import matplotlib.pyplot as plt
from scipy.stats import expon, norm


def main():
    transactions = classification.load_transactions()
    orders = classification.classify_trades(transactions)
    interarrivals = classification.calculate_interarrival_times(orders)

    arrivals = np.cumsum(interarrivals)

    time_step = 10 * 60 * 1000 #calculating hourly rates

    bins = []
    bin = []

    time = 0

    print('Processing...')

    for i, t in enumerate(arrivals):
    	if t > time + time_step:
    		jump = int(np.floor((t - time) / time_step))
    		time += jump * time_step

    		bins.extend([bin + [] * (jump - 1)])
    		bin = []
    	bin.append(orders[i])



    times = []
    rates = []
    for bin in bins:
        if len(bin) != 0:
            times.append(bin[0].start_time)
            ia = classification.calculate_interarrival_times(bin)
            loc, scale = expon.fit([i for i in ia if i > 1000])
            rates.append(scale)

    rate_returns = [rates[i + 1] / rates[i] for i in range(len(rates) - 1)]

    hours = [[] for i in range(24 * 6)]

    for i, r in enumerate(1 / np.array(rates)):
        hours[i % 24 * 6].append(r)

    plt.plot([i for i in range(24 * 6)], [np.mean(hour) for hour in hours])

    plt.show()


if __name__ == '__main__':
    main()
