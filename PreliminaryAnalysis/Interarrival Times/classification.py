import csv
import numpy as np

import matplotlib.pyplot as plt
from scipy.stats import expon, norm


class Order:
	#Order object which contains all the data for one genesis trade
	#buying true if the taker is buying, false otherwise

	def __init__(self, buyer, start_time, parent_trade = None):
		self.buyer = buyer
		self.start_time = start_time

		self.parent = parent_trade
		self.transactions = [] #transactions that make up this trade

		self.children = []

	def add_child(self, child):
		self.children.append(child)


	def add_transaction(self, transaction):
		self.transactions.append(transaction)
		self.price = transaction.price - transaction.price_change

	def calculate_price_change(self):
		change = 0

		for transaction in self.transactions:
			change += transaction.price_change

		return change

	def calaulate_volume(self):
		volume = 0

		for transaction in self.transactions:
			volume += transaction.volume

		return volume

	def weighted_price(slef):
		s = 0
		v = 0
		for t in self.transactions:
			s += t.price * t.volume
			v += t.volume

		return s / v



class Transaction:
	def __init__(self, maker, time, price, volume, n_trades, previous_time, price_change):
		self.maker = maker #True if buyer is maker, False otherwise
		self.time = time
		self.price = price
		self.volume = volume # measured in btc
		self.previous_time = previous_time
		self.price_change = price_change







def classify_trades(individual_transactions):
	orders = []

	for transaction in individual_transactions:
		parent = None


		#need to decide whether this trade is a reaction or a genesis trade
		#possible reactions are to trades within the past 400ms say as these are the transactions that need to be explained
		order = Order(not transaction.maker, transaction.time)

		#if the order is a fair time since other orders then the trade is likely not to be a reaction
		#if transaction.time - transaction.previous_time > 1000:
		#	order.add_transaction(transaction)

		#otherwise, test to see if the transaction could be part of a market order
		#TODO check that market orders always happen in the same ms, might not be true
		if transaction.time - transaction.previous_time == 0:
			possible_orders = []

			i = -0
			while len(orders) > -i:
				i -= 1
				previous_order = orders[i]
				if previous_order.start_time == transaction.time:
					possible_orders.append(previous_order)
				else:
					break

			#check whether the types of order matches

			for past_order in possible_orders:
				if past_order.buyer == (not transaction.maker):
					#should see an increase (decrease) in price if buy (sell) order
					#if (-1) ** int(not past_order.buyer) * past_order.transactions[-1].price <= (-1) ** int(not past_order.buyer) * transaction.price:
					past_order.transactions.append(transaction)
					order = None
					break

			else:
				order.add_transaction(transaction)
		else:
			order.add_transaction(transaction)

		#see if transaction is a reaction to a previous trade


		if order is not None:
			orders.append(order)


	return orders

def calculate_price_movements(orders):
	price_changes = []
	for order in orders:
		price_change = order.calculate_price_change()
		price_changes.append(price_change)

	return price_changes

def calculate_interarrival_times(orders):
	last_time = None
	interarrivals = []
	for order in orders:
		if last_time is None:
			last_time = order.start_time

		if order.parent is not None:
			interarrivals.append(order.start_time - order.parent.start_time)
		else:
			interarrivals.append(order.start_time - last_time)
		last_time = order.start_time
	return interarrivals



def load_transactions(n=-1, file='../Trade Classification/BTCUSDT201906.csv'):

	transactions = []

	previous_time = None
	previous_price = None


	with open(file, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for line in reader:
			if previous_time is None:
				previous_time = int(line['timestamp'])
				previous_price = float(line['price'])

			maker = bool(int(line['maker']))
			time = int(line['timestamp'])
			price = float(line['price'])
			volume = float(line['volume']) # (volume is measured in BTC)
			n_trades = int(line['last_trade']) - int(line['first_trade']) + 1
			price_change = price - previous_price

			transactions.append(Transaction(maker, time, price, volume, n_trades, previous_time, price_change))

			if n > 0 and len(transactions) > n:
				break

			previous_time = time
			previous_price = price

	return transactions




def main():
	print('Loading and Processing Orders')

	transactions = load_transactions()
	orders = classify_trades(transactions)
	interarrivals = calculate_interarrival_times(orders)

	buy_orders = [o for o in orders if o.buyer]
	sell_orders = [o for o in orders if not o.buyer]

	arrivals = np.cumsum(interarrivals)

	time_step = 60 * 60 * 1000 #calculating hourly rates

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
			ia = calculate_interarrival_times(bin)
			loc, scale = expon.fit([i for i in ia if i > 1000])
			rates.append(1 / scale)

	fig, ax1 = plt.subplots()




	ax1.plot((np.array(times) - bins[0][0].start_time) / time_step, rates, label='Genesis Order Rate')

	ax2 = ax1.twinx()

	ax2.plot((np.array([o.start_time for o in orders]) - orders[0].start_time) / time_step, [o.price for o in orders], label='Price', color='orange')

	fig.legend()

	fig.savefig('Order rate through time')

	plt.show()



if __name__ == '__main__':
	main()
