import sys
sys.path.append('../lib')
import exchange

import datetime
import numpy as np
import matplotlib.pyplot as plt


from PyEMD import EMD



def main():
    e = exchange.Exchange('../lib/binance.db')

    start = int(datetime.datetime(2018, 4, 1).timestamp() * 1000)
    end = int(datetime.datetime(2018, 5, 1).timestamp() * 1000)

    print('Loading order data...')

    number_of_orders = e.get_total_orders_ts('BTCUSDT', 10 * 1000, start, end)

    buy_orders  = np.array([b for s, b in number_of_orders])
    sell_orders = np.array([s for s, b in number_of_orders])

    print('Calculating IMFs')

    emd = EMD()
    IMFs = emd(buy_orders)

    N = IMFs.shape[0] + 1

    fig, axs = plt.subplots(N, sharex=True)



    for i, imf in enumerate(IMFs):
        axs[i].plot(imf)
        if i > 5:
            break




    plt.show()





if __name__ == '__main__':
    main()
