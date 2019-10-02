import sys
sys.path.append('../lib')
import exchange

import datetime

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import norm

import pandas as pd


from scipy.stats import exponweib

from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize

import csv


def calculate_parameters(start, end, step, e):
    steps = int(np.floor(((end - start).days * 24 * 60 * 60 + (end - start).seconds) / (step * 60 * 60)))
    print((end - start).days)

    parameters = []

    for i in range(steps):
        it = e.get_orders('BTCUSDT', start.timestamp() * 1000 + i * step * 1000 * 60 * 60, start.timestamp() * 1000 + (i+1) * step * 1000 * 60 * 60)
        times = []
        for order in it:
            times.append(order.time)

        sample = np.diff(times)

        print(i)

        #parameters.append([1 / m, np.exp(-c - m)])
        a, c, loc, scale = exponweib.fit(sample, loc=0, scale=1)
        parameters.append([a, c])
    return parameters



def main():
    e = exchange.Exchange('../lib/binance.db')

    start = datetime.datetime(2018, 4, 1)
    end = datetime.datetime(2019, 8, 1)

    params = calculate_parameters(start, end, 24, e)

    print(np.mean(params, axis=0), np.var(params, axis=0))

    #plt.plot([p[0] for p in params])
    fig, ax = plt.subplots(1)

    with open('parameters.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for p in params:
            writer.writerow([start] + p)
            start = start + datetime.timedelta(days=1)


    ax2 = ax.twinx()
    ax.plot([p[0] for p in params])
    ax2.plot([p[1] for p in params], color='orange')
    plt.show()


if __name__ == '__main__':
    main()
