import sys
sys.path.append('../lib')
import exchange

import datetime

from PyEMD import EEMD
import numpy as np
import matplotlib.pyplot as plt

def calculate_returns(prices):
    returns = np.ones(len(prices))
    previous_price = prices[0]
    for i, price in enumerate(prices[1:]):
        returns[i + 1] = price / previous_price
        previous_price = price

    return returns

def main():

    #load data

    e = exchange.Exchange('../lib/binance.db')

    start = int(datetime.datetime(2018, 7, 1).timestamp() * 1000)
    end = int(datetime.datetime(2019, 7, 1).timestamp() * 1000)

    print('Loading order data...')

    number_of_orders, prices = e.get_total_orders_ts('BTCUSDT', 60 * 60 * 1000, start, end) #hourly data

    print('done')

    buy_orders  = np.array([b for s, b in number_of_orders])
    sell_orders = np.array([s for s, b in number_of_orders])

    t = [i for i, o in enumerate(buy_orders)]

    eemd = EEMD()
    emd = eemd.EMD

    eIMFs = eemd.eemd(buy_orders - sell_orders)
    n = eIMFs.shape[0]




    fig, axs = plt.subplots(n + 3, figsize=(12,9), sharex=True)

    axs[0].plot(prices)
    axs[0].set_ylabel('Price')

    axs[1].plot(buy_orders - sell_orders, color='g')
    axs[1].set_ylabel('Orders - (Buy - sell)')

    axs[2].plot(calculate_returns(prices))

    for i in range(n):

        axs[i + 3].plot(eIMFs[i], color='g')
        axs[i + 3].set_ylabel('eIMF ' + str(i + 1))


    plt.xlabel("Time /days")
    #plt.tight_layout()


    plt.show()


if __name__ == '__main__':
    main()
