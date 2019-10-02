import sys
sys.path.append('../lib')
import exchange

import datetime

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import norm

import pandas as pd

from transition_prob_through_time import transition_probabilities

from sklearn.linear_model import LinearRegression

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def inv_sigmoid(x):
    return np.log(x) - np.log(1 - x)


def sort_data(series, k):
    y = series[k:]
    x = np.zeros((series.shape[0] - k, k * series.shape[1]))

    for i in range(series.shape[0] - k):
        x[i] = np.reshape(series[i:i+k], -1)

    return x, y





def main():
    e = exchange.Exchange('../lib/binance.db')

    start = datetime.datetime(2018, 4, 1)

    days = [start + datetime.timedelta(days = i) for i in range(460)]

    daily_returns = []
    daily_prices = []
    rates = []
    p_00 = []
    p_11 = []

    EMA = []
    alpha = 2 / (50 + 1)

    price = None


    for start, end in zip(days[:-1], days[1:]):
        print(start)
        it = e.get_orders('BTCUSDT', start.timestamp() * 1000, end.timestamp() * 1000)
        trade_data = {'price': [], 'time': [], 'side': []}
        returns = []
        prices = []

        for order in it:
            if price is None:
                r = 1
                price = order.end_price
                continue
            elif price != order.end_price:
                r = order.end_price / price
            else:
                continue

            trade_data['price'].append(order.end_price)
            trade_data['time'].append(order.time)
            trade_data['side'].append(order.buyer)



            price = order.end_price
            returns.append(r)
            prices.append(order.end_price)


        trade_data = pd.DataFrame(trade_data)

        trade_data['price_change'] = np.log(np.concatenate(([1], trade_data['price'].values[1:] / trade_data['price'].values[:-1])))

        movement = np.zeros(trade_data.shape[0])
        movement[trade_data['price_change'] > 0] = 1
        movement[trade_data['price_change'] < 0] = -1

        chain = movement[movement != 0]
        P, states  = transition_probabilities(chain)

        try:
            p_11.append(P[states[1]][states[1]])
            p_00.append(P[states[-1]][states[-1]])
        except:
            continue


        daily_returns.append(np.log(np.mean(np.abs(np.log(returns)))))
        rates.append(24 * 60 * 60 * 1000 / len(returns)) #average length of interarrival time

    n_days = len(rates)
    test_start = 400
    test_len = 50
    series = np.zeros((n_days, 4))

    series[:, 0] = inv_sigmoid(np.array(p_00))
    series[:, 1] = inv_sigmoid(np.array(p_11))
    series[:, 2] = np.array(daily_returns)
    series[:, 3] = np.log(np.array(rates))

    k = 14
    x, y = sort_data(series[:test_start], k)


    reg = LinearRegression().fit(x, y)


    x, y = sort_data(series[test_start - k : test_start + test_len], k)



    prediction = reg.predict(x)

    fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2)

    errors = y - prediction

    print(np.mean(errors, axis=0), np.cov(errors, rowvar=0))



    plt.show()


if __name__ == '__main__':
    main()
