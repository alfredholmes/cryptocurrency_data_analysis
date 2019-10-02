import ijson


def main():
	with open('BTCUSDT.json', 'r') as f:
		trades = ijson.items(f, 'item')

		for trade in trades:
			print(trade['time'], trade['price'])
			print(trade)


if __name__ == '__main__':
	main()