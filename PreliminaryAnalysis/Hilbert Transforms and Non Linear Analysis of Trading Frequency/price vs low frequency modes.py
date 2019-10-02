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
    #end = int(datetime.datetime(2018, 8, 1).timestamp() * 1000)
    end = int(datetime.datetime(2019, 7, 1).timestamp() * 1000)

    print('Loading order data...')

    number_of_orders, prices = e.get_total_orders_ts('BTCUSDT', 24 * 60 * 60 * 1000, start, end) #hourly data

    print('done')

    buy_orders  = np.array([b for s, b in number_of_orders])
    sell_orders = np.array([s for s, b in number_of_orders])


    t = [i for i, o in enumerate(buy_orders)]

    eemd = EEMD()
    emd = eemd.EMD



    eIMFs_buys = eemd.eemd(buy_orders)
    eIMFs_sells = eemd.eemd(sell_orders)

    if eIMFs_buys.shape[0] != eIMFs_sells.shape[0]:
        print('size mismatch')

    n = min(eIMFs_buys.shape[0], eIMFs_sells.shape[0])




    fig, axs = plt.subplots(3, figsize=(12,9), sharex=True)

    axs[0].plot(prices)
    axs[0].set_ylabel('Price')

    buys = np.sum(eIMFs_buys[1:-2], axis=0)
    sells = np.sum(eIMFs_sells[1:-2], axis=0)

    axs[1].plot(buys, color='g')
    axs[1].plot(sells, color='r')

    axs[2].plot(calculate_returns(prices), color='b')


    ax3 = axs[2].twinx()
    ax3.plot((0, len(prices)), (0.5, 0.5))
    ax3.plot(buys - sells)

    plt.xlabel("Time /days")






    #plt.tight_layout()


    plt.show()


if __name__ == '__main__':
    main()
