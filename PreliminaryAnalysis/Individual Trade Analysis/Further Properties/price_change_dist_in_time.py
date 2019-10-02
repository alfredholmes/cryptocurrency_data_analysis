import ijson
import numpy as np
import matplotlib.pyplot as plt
def main():
	with open('BTCUSDT.json', 'r') as f:
		trades = ijson.items(f, 'item')

		previous_price = None
		previous_time = None
		#times = [(0, 500), (500, 1000), (1000, 2000), (2000, 8000)]
		times = [(0, 2), (2, 4), (4, 8), (8, 16), (16, 32), (32, 64)]
		changes = {time: [] for time in times}
		interarrivals = {time: [] for time in times}
		volumes = {time: [] for time in times}


		for i, trade in enumerate(trades):
			if i > 10000:
				break
			#if previous_price is not None and int(trade['time']) - previous_time > 2000:
			if previous_price is not None:
				interarrival = int(trade['time']) - previous_time
				for i, time in enumerate(times):
					price_change = float(trade['price']) - float(previous_price)
					if time[0] < interarrival and interarrival <= time[1]:

						changes[time].append(price_change)
						interarrivals[time].append(interarrival)
						volumes[time].append(float(trade['qty']))


			previous_price = float(trade['price'])
			previous_time = int(trade['time'])



		plt.show()

if __name__ == '__main__':
	main()