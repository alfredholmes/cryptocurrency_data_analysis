import sys
sys.path.append('../lib')
import exchange

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import datetime

def moving_average(a, n=1000) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def main():
    data = pd.read_csv('parameters.csv', header=None)

    start = datetime.datetime.strptime(data[0].iloc[0], '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(data[0].iloc[-1], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=1)

    distance_to_ma = []
    step = 24

    e = exchange.Exchange('../lib/binance.db')

    days = (end - start).days

    for i in range((end - start).days):
        print(i, '/' , days)

        it = e.get_orders('BTCUSDT', start.timestamp() * 1000 + i * step * 1000 * 60 * 60, start.timestamp() * 1000 + (i+1) * step * 1000 * 60 * 60)

        current_prices = []
        for order in it:
            current_prices.append(order.average_price)

        distance_to_ma.append(np.mean(np.abs(current_prices)[50 - 1:] - moving_average(current_prices, 50)))


    plt.scatter(distance_to_ma, data[2])


    plt.show()

if __name__ == '__main__':
    main()
