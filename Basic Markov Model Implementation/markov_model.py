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


def asim_variance(P, n = int(24 * 60 * 60 * 1000 / 200)):
    stat_dist = np.array([1, P[0][1] / P[1][0]]) / (1 + P[0][1] / P[1][0])

    lim = np.array((stat_dist, np.flip(stat_dist)))

    current_P = P

    ret = 1 - (stat_dist[0] - stat_dist[1]) ** 2


    for i in range(n):
        cov = stat_dist[0] * (current_P[0][0] - current_P[0][1]) + stat_dist[1] * (current_P[1][1] - current_P[1][0]) - (stat_dist[0] - stat_dist[1]) ** 2
        current_P = np.matmul(P, current_P)

        ret += 2 * cov


    return ret


def sort_data(series, k):
    y = series[k:]
    x = np.zeros((series.shape[0] - k, k * series.shape[1]))

    for i in range(series.shape[0] - k):
        x[i] = np.reshape(series[i:i+k], -1)

    return x, y


def return_cdf(x, p_00, p_11, expected_return, trade_rate, n =int(24 * 60 * 60 * 1000 / 200)):
    P = np.array([[p_00, 1 - p_00],[1 - p_11, p_11]])
    stat_dist = np.array([1, P[0][1] / P[1][0]]) / (1 + P[0][1] / P[1][0])
    var = asim_variance(P, n)
    x = x * expected_return

    T = 24 * 60 * 60 * 1000

    ret = np.zeros(x.shape[0])

    for i in range(1, n):

        #n_prob = norm.cdf((T - (i + 0.5) * trade_rate) / (trade_rate * np.sqrt(i + 0.5))) - norm.cdf((T - (i - 0.5) * trade_rate) / (trade_rate * np.sqrt(i - 0.5)))
        #n_prob = norm.cdf(i + 0.5, loc=24 * 60 * 60 * 1000 / trade_rate, scale=24 * 60 * 60 * 1000 / trade_rate) - norm.cdf(i - 0.5, loc=24 * 60 * 60 * 1000 / trade_rate, scale=24 * 60 * 60 * 1000 / trade_rate)
        n_prob = poisson.pmf(i, mu = 24 * 60 * 60 * 1000 / trade_rate)
        ret += norm.cdf((x - i * (stat_dist[0] - stat_dist[1])) / (2 * np.sqrt(var * i))) * n_prob

    return ret


def simulate_return(p_00, p_11, expected_return, trade_rate):
    P = np.array([[p_00, 1 - p_00],[1 - p_11, p_11]])
    stat_dist = np.array([1, (1 - p_11) / (1 - p_00)]) / (1 + (1 - p_11) / (1 - p_00))

    ret = 0
    T = 0

    X = 1 if uniform.rvs() < stat_dist[0] else -1
    while T < 24 * 60 * 60 * 1000:
        ret += X
        T += expon.rvs(scale=trade_rate)
        X = 1 if uniform.rvs() < P[0 if X == 1 else 1][0] else -1
    return ret * expected_return

def calculate_normal_params(y):
    p_00 = sigmoid(y[0])
    p_11 = sigmoid(y[1])
    trade_movement_average = np.exp(y[2])
    average_trade_time = np.exp(y[3])



    P = np.array([[p_00, 1 - p_00], [1 - p_11, p_11]])
    stat_dist = np.array([1, P[0][1] / P[1][0]]) / (1 + P[0][1] / P[1][0])

    print(stat_dist)

    mu = (stat_dist[0] - stat_dist[1]) * trade_movement_average * 24 * 1000 * 60 * 60 / average_trade_time
    ns = np.cumsum(np.ones(int(1.5 * 24 * 1000 * 60 * 60 / average_trade_time)))
    as_var = asim_variance(P)

    var = np.sum(4 * ns * as_var * poisson.pmf(ns, mu=24 * 60 * 60 * 1000 / average_trade_time)) * trade_movement_average ** 2

    return mu, var


def main():
    e = exchange.Exchange('../lib/binance.db')

    start = datetime.datetime(2018, 5, 1)

    days = [start + datetime.timedelta(days = i) for i in range(10)]

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

        print(np.mean(np.log(increases)), np.mean(np.log(decreases)), np.mean(np.abs(np.log(returns))))


        trade_data = pd.DataFrame(trade_data)

        trade_data['price_change'] = np.log(np.concatenate(([1], trade_data['price'].values[1:] / trade_data['price'].values[:-1])))

        movement = np.zeros(trade_data.shape[0])
        movement[trade_data['price_change'] > 0] = 1
        movement[trade_data['price_change'] < 0] = -1

        print(np.sum(movement[movement == 1]) / movement.shape[0])

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
    test_start = 2
    test_len = 8
    series = np.zeros((n_days, 4))

    series[:, 0] = inv_sigmoid(np.array(p_00))
    series[:, 1] = inv_sigmoid(np.array(p_11))
    series[:, 2] = np.log(daily_returns)
    series[:, 3] = np.log(rates)

    k = 1
    x, y = sort_data(series[:test_start], k)


    reg = LinearRegression().fit(x, y)


    x, y = sort_data(series[test_start - k : test_start + test_len], k)


    x = np.linspace(-2,2, 100)
    mean = 0
    variance = 0
    for i in range(7):
        mu, var = calculate_normal_params(y[i])
        mean += mu
        variance += var

        print(mu, variance)


    plt.plot(np.exp(x), norm.pdf(x, loc = mean, scale = np.sqrt(variance)))

    plt.show()


if __name__ == '__main__':
    main()
