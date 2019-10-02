import csv
import numpy as np
import matplotlib.pyplot as plt
import datetime



def main():
	symbol = 'BTCUSDT'

	with open('../Binance/' + symbol + '.csv', 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		previous_price = 0
		start = int(datetime.datetime.timestamp(datetime.datetime(2019, 6, 1))) * 1000 - 365 * 24 * 60 * 60 * 1000
		time_step = 1
		previous_time = start
		trades = 0
		price_difference = 0
		price_difference_sq = 0
		data = {'mean': [], 'variance': [], 'trades': []}
		for line in reader:
			if int(line['Timestamp']) > previous_time + 1000 * 60 * 60 * time_step:
				previous_time += np.floor((int(line['Timestamp']) - previous_time) / (1000 * 60 * 60 * time_step)) * 1000 * 60 * 60 * time_step
				mean = price_difference / trades
				variance = price_difference_sq / trades - mean ** 2
				data['mean'].append(mean)
				data['variance'].append(variance)
				data['trades'].append(trades)
				price_difference = price_difference_sq = trades = 0


			trades += 1
			price_difference += float(line['Price']) - previous_price
			price_difference_sq += (float(line['Price']) - previous_price)**2
			previous_price = float(line['Price'])


	plt.figure()
	plt.plot(data['mean'][1:], label='Sample Mean')
	plt.plot([0, len(data['mean']) - 1], [np.mean(data['mean'])] * 2, label='Average:'  + str(np.mean(data['mean'])))

	plt.xlabel('Time')
	plt.ylabel('Mean')

	plt.savefig(symbol + 'mean')

	plt.figure()
	plt.plot(data['variance'][1:])
	plt.xlabel('Time')
	plt.ylabel('Variance')

	plt.savefig(symbol + 'variance')


	plt.figure()
	plt.plot(data['trades'][1:])
	plt.xlabel('Time')
	plt.ylabel('Number of Trades')


	plt.savefig(symbol + 'trades')



	plt.show()



if __name__ == '__main__':
	main()