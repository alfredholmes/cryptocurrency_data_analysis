import sys
sys.path.append('../lib')
import exchange

import datetime

import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import norm
from scipy.stats import uniform
from scipy.stats import expon
from scipy.stats import poisson

from scipy.integrate import quad

import pandas as pd

from transition_prob_through_time import transition_probabilities

from sklearn.linear_model import LinearRegression


def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def inv_sigmoid(x):
    return np.log(x) - np.log(1 - x)


def asim_variance(P, average_increase, average_decrease, n = int(24 * 60 * 60 * 1000 / 200)):
    stat_dist = np.array([1, P[0][1] / P[1][0]]) / (1 + P[0][1] / P[1][0])

    lim = np.array((stat_dist, np.flip(stat_dist)))

    current_P = P

    ret = average_increase ** 2 + average_decrease ** 2 - (stat_dist[0] * average_increase - stat_dist[1] * average_increase) ** 2


    for i in range(n):
        cov = stat_dist[0] * (current_P[0][0] * average_increase ** 2 - current_P[0][1] * average_increase * average_decrease) + stat_dist[1] * (current_P[1][1] * average_decrease ** 2 - current_P[1][0] * average_increase * average_decrease) - (stat_dist[0] * average_increase - stat_dist[1] * average_decrease) ** 2
        current_P = np.matmul(P, current_P)
        if np.abs(cov) < 2 ** -16:
            break
        ret += 2 * cov

    return ret


def sort_data(series, k):
    y = series[k:]
    x = np.zeros((series.shape[0] - k, k * series.shape[1]))

    for i in range(series.shape[0] - k):
        x[i] = np.reshape(series[i:i+k], -1)

    return x, y


def calculate_normal_params(y):
    p_00 = sigmoid(y[0])
    p_11 = sigmoid(y[1])
    average_increase = np.exp(y[2])
    average_decrease = np.exp(y[3])
    average_trade_time = np.exp(y[4])



    P = np.array([[p_00, 1 - p_00], [1 - p_11, p_11]])
    stat_dist = np.array([1, P[0][1] / P[1][0]]) / (1 + P[0][1] / P[1][0])


    mu = (stat_dist[0] * average_increase - stat_dist[1] * average_decrease) * 24 * 1000 * 60 * 60 / average_trade_time
    ns = np.cumsum(np.ones(int(1.5 * 24 * 1000 * 60 * 60 / average_trade_time)))
    as_var = asim_variance(P, average_increase, average_decrease)

    var = np.sum(4 * ns * as_var * poisson.pmf(ns, mu=24 * 60 * 60 * 1000 / average_trade_time)) ** 2

    return mu, var


def predict(initial, model, n):
    input = initial.copy()
    output = []
    for i in range(n):
        next = model.predict(input)
        input[:-1] = input[1:]
        input[-1] = next
        output.append(next[0])

    return output




def main():
    e = exchange.Exchange('../lib/binance.db')

    start = datetime.datetime(2018, 4, 1)

    days = [start + datetime.timedelta(days = i) for i in range(400)]

    daily_returns = []
    daily_increases = []
    daily_decreases = []

    daily_price = []
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

        increases = []
        decreases = []

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

            if r > 1:
                increases.append(r)
            else:
                decreases.append(r)

        daily_decreases.append(np.mean(np.abs(np.log(decreases))))
        daily_increases.append(np.mean(np.abs(np.log(increases))))


        daily_price.append(order.end_price)

        trade_data = pd.DataFrame(trade_data)

        trade_data['price_change'] = np.log(np.concatenate(([1], trade_data['price'].values[1:] / trade_data['price'].values[:-1])))

        movement = np.zeros(trade_data.shape[0])
        movement[trade_data['price_change'] > 0] = 1
        movement[trade_data['price_change'] < 0] = -1


        chain = movement[movement != 0]
        P, states  = transition_probabilities(chain)



        try:
            p_00.append(P[states[1]][states[1]])
            p_11.append(P[states[-1]][states[-1]])
        except:
            continue


        daily_returns.append(np.mean(np.abs(np.log(returns))))
        rates.append(24 * 60 * 60 * 1000 / len(returns)) #average length of interarrival time

    n_days = len(rates)
    test_start = 250
    test_len = 49
    series = np.zeros((n_days, 5))

    series[:, 0] = inv_sigmoid(np.array(p_00))
    series[:, 1] = inv_sigmoid(np.array(p_11))
    series[:, 2] = np.log(daily_increases)
    series[:, 3] = np.log(daily_decreases)
    series[:, 4] = np.log(rates)

    k = 1
    x, y = sort_data(series[:test_start], k)
    reg = LinearRegression().fit(x, y)

    initial = x[-k:]
    prediction = np.array(predict(initial, reg, 49))

    x = np.linspace(np.log(0.5),np.log(1.5), 1000)
    means = []
    variances = []


    for i in range(prediction.shape[0]):
        print('calculating day', i)
        mu, var = calculate_normal_params(prediction[i])
        means.append(mu)
        variances.append(var)


    means = np.cumsum(means)
    vars = np.cumsum(variances)

    start_price = daily_price[test_start - 1]

    prices = daily_price[test_start: test_start + test_len]


    plt.plot(prices)
    plt.plot(np.exp(means) * start_price)
    plt.plot(np.exp(means + 3 * vars) * start_price)
    plt.plot(np.exp(means - 3 * vars) * start_price)

    plt.show()


if __name__ == '__main__':
    main()
