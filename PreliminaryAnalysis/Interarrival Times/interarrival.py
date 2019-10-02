import csv
import datetime

import matplotlib.pyplot as plt
import numpy as np

import random

from scipy.stats import expon

def main():
	symbol = 'BTCUSDT'

	with open('../Binance/' + symbol + '.csv', 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		start = int(datetime.datetime.timestamp(datetime.datetime(2019, 6, 1))) * 1000 - 365 * 24 * 60 * 60 * 1000
		time_step = 1
		previous_time = start
		last_time = start
		
		data = {'interarrivals': {}, 'volume': []}

		interarrivals = []
		i = 0
		volume = 0

		for line in reader:
			

			if int(line['Timestamp']) > previous_time + 1000 * 60 * 60 * time_step:
				data['interarrivals'][previous_time] = interarrivals
				data['volume'].append(volume)
				
				interarrivals = []
				volume = 0

				previous_time += np.floor((int(line['Timestamp']) - previous_time) / (1000 * 60 * 60 * time_step)) * 1000 * 60 * 60 * time_step
				i += 1
				if i > 2000:
					break
			volume += float(line['Volume'])

			interarrival = int(line['Timestamp']) - last_time
			if interarrival < 0:
				continue

			interarrivals.append(interarrival)
			last_time = int(line['Timestamp'])

	start_times = [1000]	

	fig, ax1 = plt.subplots()
	for start_time in start_times:
		rates = []
		for time, hour in data['interarrivals'].items():

			_, scale = expon.fit([t for t in hour if t > start_time])

			rates.append(1 / scale)


		#ax1.plot(rates, label=start_time)


	ax2 = ax1.twinx()

	#ax2.bar([x for x in range(len(data['volume']))], data['volume'], width=1, color='orange', alpha=0.3)

	#plt.savefig('Tail Rate against volume through time')

	#ax1.legend()

	plt.figure()

	plt.scatter(np.log([r for i, r in enumerate(rates) if i % 24 == 0]), np.log([v for i, v in enumerate(data['volume']) if i % 24 == 0]))

	plt.savefig('volume against rate')



	plt.show()
	
if __name__ == '__main__':
	main()