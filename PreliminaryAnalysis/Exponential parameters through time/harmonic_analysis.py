import parameter_estimation
import sys
sys.path.append('../lib')
import exchange

import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import hilbert


from PyEMD import EEMD

def main():
    e = exchange.Exchange('../lib/binance.db')

    start = datetime.datetime(2018, 8, 1)
    end = datetime.datetime(2019, 8, 1)

    params = parameter_estimation.calculate_parameters(start, end, 6, e)

    eemd = EEMD()
    emd = eemd.EMD

    eIMFs_rate = eemd.eemd(np.array([p[1] for p in params]))

    fig, axs = plt.subplots(eIMFs_rate.shape[0], figsize=(12, eIMFs_rate.shape[0] * 3))
    rate = np.zeros(eIMFs_rate.shape[1])

    for ax, IMF in zip(axs, eIMFs_rate):
        #ax.plot(IMF)
        ax.plot(IMF)
        analytic_signal = hilbert(IMF)
        phase = np.unwrap(np.angle(analytic_signal))
        freq = np.diff(phase) / (2 * np.pi * 0.25)
        print(np.mean(1 / freq))

    plt.tight_layout()
    plt.show()



if __name__ == '__main__':
    main()
