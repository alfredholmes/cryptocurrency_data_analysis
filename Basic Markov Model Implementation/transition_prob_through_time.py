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

        p_00 = []
        p_11 = []

        prices = []



        for start, end in zip(times[:-1], times[1:]):
            print(start)
            it = e.get_orders('BTCUSDT', start.timestamp() * 1000, end.timestamp() * 1000)
            trade_data = {'price': [], 'time': [], 'side': []}

            for order in it:
                trade_data['price'].append(order.end_price)
                trade_data['time'].append(order.time)
                trade_data['side'].append(order.buyer) #True if market order is a buy

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
                pass

            prices.append(np.mean(trade_data['price']))



        #fig, ax1 = plt.subplots()
        #ax2 = ax1.twinx()

        #ax1.plot(prices, color='blue')
        #ax2.plot(p_11, color='green', label='p_11')
        #ax2.plot(p_00, color='red', label='p_00')
        #ax2.legend()

        #ax1.set_xlabel('Day')
        #ax1.set_ylabel('BTC Price')
        #ax2.set_ylabel('Probability')
        plt.figure()
        plt.hist(np.diff(p_00), 50, density=True)
        loc, scale = norm.fit(np.diff(p_00))
        x = np.linspace(np.min(np.diff(p_00)), np.max(np.diff(p_00)), 100)
        plt.plot(x, norm.pdf(x, loc=loc, scale=scale))

        plt.figure()
        plt.hist(np.diff(p_11), 50, density=True)
        x = np.linspace(np.min(np.diff(p_11)), np.max(np.diff(p_11)), 100)
        loc, scale = norm.fit(np.diff(p_11))
        plt.plot(x, norm.pdf(x, loc=loc, scale=scale))

        plt.show()



if __name__ == '__main__':
    main()
