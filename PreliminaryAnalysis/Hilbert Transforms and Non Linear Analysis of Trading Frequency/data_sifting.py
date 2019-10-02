import sys
sys.path.append('../lib')
import exchange

import datetime
import numpy as np
import matplotlib.pyplot as plt

from scipy.interpolate import interp1d
from scipy.signal import argrelextrema


def find_local_maxima_minima(data):

    min = argrelextrema(data, np.greater)
    max = argrelextrema(data, np.less)

    min = np.insert(min, 0, 0)
    max = np.insert(max, 0, 0)
    min = np.append(min, len(data) - 1)
    max = np.append(max, len(data) - 1)

    return min, max


def sd(data1, data2):
    return np.sum(np.power(np.subtract(data1, data2), 2) / np.power(data1, 2)) / len(data1)

def stopping_criterion(data, th1, th2):
    minima, maxima = find_local_maxima_minima(data)

    min = interp1d([i for i in minima], [data[i] for i in minima], kind='cubic')
    max = interp1d([i for i in maxima], [data[i] for i in maxima], kind='cubic')

    x = np.linspace(0.1, len(data) - 1.1, len(data))
    sigma = np.abs((max(x) + min(x)) / (max(x) - min(x)))

    return (sigma < th1).sum() / (len(x)), (sigma < th2).sum() / (len(x))

def sift(data):
    minima, maxima = find_local_maxima_minima(data)

    min = interp1d([i for i in minima], [data[i] for i in minima], kind='cubic')
    max = interp1d([i for i in maxima], [data[i] for i in maxima], kind='cubic')

    return np.array([d - (max(i) + min(i) / 2) for i, d in enumerate(data)])

def zero_crosses(data):
    previous_above = None
    crosses = 0
    for x in data:
        if previous_above is None:
            previous_above = x > 0
        if previous_above != x > 0:
            crosses += 1
        previous_above = x > 0

    return crosses

def calculate_component(data, th1 = 0.05, th2 = 10 * 0.05, alpha = 0.05):
    sifted_1 = data
    sifted_2 = sift(data)

    should_stop = False

    below_th1 = 0
    below_th2_th2 = 0


    IMF = False

    while (below_th1 <= 0.99 or below_th2 <= (1 - alpha)) and not IMF:
        sifted = sift(sifted_2)
        sifted_1 = sifted_2
        sifted_2 = sifted
        below_th1, below_th2 = stopping_criterion(sifted_2, th1, th2)

        crosses = zero_crosses(sifted_2)
        minima, maxima = find_local_maxima_minima(sifted_2)

        if np.abs(crosses - len(minima) - len(maxima)) < 5:
            IMF = True

        print('\t', below_th1, below_th2, crosses, len(minima), len(maxima))


    return sifted_1


def generate_components(data, max = 3):
    current = data
    minima, maxima = find_local_maxima_minima(data)


    components = [data]

    i = 0


    while len(minima) > 3 and i < max:
        next_component = calculate_component(current)
        components.append(next_component)
        current = current - next_component
        minima, maxima = find_local_maxima_minima(data)
        i += 1
        print(i, len(minima))


    components.append(current)

    return components


def main():


    e = exchange.Exchange('../lib/binance.db')

    start = int(datetime.datetime(2018, 4, 1).timestamp() * 1000)
    end = int(datetime.datetime(2018, 7, 1).timestamp() * 1000)

    print('loading orders')

    number_of_orders = e.get_total_orders_ts('BTCUSDT', 24 * 60 * 60 * 1000, start, end)

    buy_orders  = np.array([b for s, b in number_of_orders])
    sell_orders = np.array([s for s, b in number_of_orders])


    print('calculating components')


    components = generate_components(buy_orders, 10)


    fig, axs = plt.subplots(len(components), sharex=True)

    for i, c in enumerate(components):
        axs[i].plot(c)

    plt.show()








if __name__ == '__main__':
    main()
