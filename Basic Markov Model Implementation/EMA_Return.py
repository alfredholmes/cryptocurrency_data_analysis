import sys
sys.path.append('../lib')
import exchange

import datetime

import numpy as np
import matplotlib.pyplot as plt


import pandas as pd

from scipy.stats import norm



def transition_probabilities(chain, offset=1):
    states = np.array([s for s in set(chain)])

    state_space = {s: i for i, s in enumerate(states)}
    transition_matrix = np.zeros((states.shape[0], states.shape[0]))
    for i in states:
        total_in_state = np.sum(chain == i) - np.sum(chain[-offset:] == i)
        relevant_states = np.concatenate(([False] * offset, (chain == i)[:-offset]))
        for j in states:
            transition_matrix[state_space[i]][state_space[j]] = np.sum(chain[relevant_states] == j) / total_in_state
    return transition_matrix, state_space




def main():
        e = exchange.Exchange('../lib/binance.db')

        times = [datetime.datetime(2018, 4, 1) + datetime.timedelta(days=i) for i in range(500)]

        start = datetime.datetime(2019, 4, 2)
        end = datetime.datetime(2019, 4, 28)


        EMA = []
        alpha = 0.3

        returns = []
        previous_price = None


        it = e.get_orders('BTCUSDT', start.timestamp() * 1000, end.timestamp() * 1000)


        for order in it:
            if previous_price is None:
                previous_price = order.end_price
                continue
            elif np.abs(np.log(previous_price / order.end_price)) < 10 **-5:
                continue
            if len(EMA) == 0:
                EMA.append(np.log(order.end_price / previous_price))
            else:
                EMA.append(alpha * np.log(order.end_price / previous_price) + (1 - alpha) * EMA[-1])



            r = order.end_price / previous_price
            previous_price = order.end_price
            returns.append(np.log(r))

        r_var = np.var(returns)
        e_var = np.var(EMA)

        #limits = [[-3 * np.sqrt(e_var), 3 * np.sqrt(e_var)], [-3 * np.sqrt(r_var), 3 * np.sqrt(r_var)]]
        limits = [[-0.0003, 0.0003], [-0.001, 0.001]]
        plt.hist2d(EMA[:-1], returns[1:], bins = 1000, range=limits)
        plt.ylabel('Next return')
        plt.xlabel('Return EMA')
        plt.show()




if __name__ == '__main__':
    main()
