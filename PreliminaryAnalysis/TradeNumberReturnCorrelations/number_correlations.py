import sys
sys.path.append('../../lib')
import exchange

import datetime

import numpy as np
import matplotlib.pyplot as plt

from stldecompose import decompose

from scipy.stats import norm, skewnorm

def calculate_returns(prices):
    returns = np.ones(len(prices))
    previous_price = prices[0]
    for i, p in enumerate(prices):
        returns[i] = p / previous_price
        previous_price = p

    return returns

def get_correlation_coef(arr1, arr2, n, positive):

    if positive:
        corrs = np.zeros(n + 1)
    else:
        corrs = np.zeros(2 * n + 1)


    if not positive:
        for i in range(1, n + 1):
            x = np.array((arr1[:-i],arr2[i:]))
            corrs[i - 1] = np.corrcoef(x)[0, 1]

        x = np.array((arr1, arr2))
        corrs[n] = np.corrcoef(x)[0, 1]

        for i in range(1, n + 1):
            x = np.array((arr1[i:],arr2[:-i]))
            corrs[n + i] = np.corrcoef(x)[0, 1]

        return np.linspace(-n, n, 2 * n + 1), corrs

    if positive:
        x = np.array((arr1, arr2))
        corrs[0] = np.corrcoef(x)[0, 1]

        for i in range(1, n + 1):
            x = np.array((arr1[i:],arr2[:-i]))
            corrs[n + i] = np.corrcoef(x)[0, 1]

        return np.linspace(0, n, n + 1), corrs

def main():

    #load data

    e = exchange.Exchange('../../lib/binance.db')

    start = int(datetime.datetime(2018, 4, 1).timestamp() * 1000)
    end = int(datetime.datetime(2019, 5, 1).timestamp() * 1000)
    #end = int(datetime.datetime(2018, 5, 1).timestamp() * 1000)

    print('Loading order data...')

    number_of_orders, prices = e.get_total_orders_ts('BTCUSDT', 60 * 60 * 1000 * 6, start, end) #hourly data

    print('done')

    buy_orders = np.array([b for s, b in number_of_orders])
    sell_orders = np.array([s for s, b in number_of_orders])


    buy_orders[buy_orders <= 0] = np.mean(buy_orders)
    sell_orders[sell_orders <= 0] = np.mean(sell_orders)


    returns = np.array(calculate_returns(prices))

    returns_decomp = decompose(returns, period=24 * 7)


    sa_returns = returns_decomp.trend + returns_decomp.resid

    buy_orders_decomp = decompose(buy_orders, period=24 * 7)
    sa_buy_orders = buy_orders_decomp.trend + buy_orders_decomp.resid



    sell_orders_decomp = decompose(sell_orders, period=24 * 7)
    sa_sell_orders = sell_orders_decomp.trend + sell_orders_decomp.resid

    x, corrs = get_correlation_coef(buy_orders_decomp.resid - sell_orders_decomp.resid, returns_decomp.resid, 28, False)


    plt.bar(x, corrs)



    plt.show()


if __name__ == '__main__':
    main()
