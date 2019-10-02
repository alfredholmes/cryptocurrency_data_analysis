import sys
sys.path.append('../lib')
import exchange

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import datetime
from scipy.optimize import minimize
from sklearn.linear_model import LinearRegression
from scipy.stats import norm

def moving_average(a, n=1000) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def main():
    e = exchange.Exchange('../lib/binance.db')


    times = [datetime.datetime(2018, 4, 1) + i * datetime.timedelta(hours=1) for i in range(10000)]

    variances = []
    prices = []
    average_distances = []
    order_average = 25
    for start, end in zip(times[:-1], times[1:]):
        print(start)
        it = e.get_orders('BTCUSDT', start.timestamp() * 1000, end.timestamp() * 1000)
        trades = {'price': [], 'time': []}



        for order in it:
            trades['time'].append(order.time)
            trades['price'].append(order.average_price)


        trades = pd.DataFrame(trades)
        if trades['time'].values.shape[0] == 0:
            continue
        price_changes = np.diff(trades['price'])
        average_distances.append(np.mean(np.abs(trades['price'][order_average - 1:] - moving_average(trades['price'].values, order_average))))
        variances.append(np.var(price_changes))

    fig, (ax1, ax2) = plt.subplots(2)

    fig.suptitle('Variance against distance to moving average analysis')

    lad = np.log(average_distances)
    lv = np.log(variances)

    reg = LinearRegression().fit(lad.reshape(-1, 1), lv)

    ax1.scatter(lad, lv, alpha=0.3)
    ax1.set_ylabel('log variance')
    ax1.set_xlabel('log distance to moving average')
    x = np.linspace(np.min(lad), np.max(lad), 2)
    ax1.plot(x, reg.predict(x.reshape(-1, 1)), color='orange')

    resid = lv - reg.predict(lad.reshape(-1, 1))
    x = np.linspace(1 / resid.shape[0], 1 - 1 / resid.shape[0], resid.shape[0] - 1)
    ax2.scatter(norm.ppf(x),np.sort(resid)[1:])
    reg = LinearRegression().fit(norm.ppf(x).reshape(-1, 1), np.sort(resid)[1:])
    ax2.plot(norm.ppf(x), reg.predict(norm.ppf(x).reshape(-1, 1)), color='orange')

    ax2.set_ylabel('Order Statistic')


    plt.tight_layout()
    plt.show()



if __name__ == '__main__':
    main()
