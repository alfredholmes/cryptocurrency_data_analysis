from scipy.stats import uniform

import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import minimize
from scipy.stats import exponweib


def calculate_parameters(interarrivals):
    sample = np.array(interarrivals)
    x = np.linspace(0, 1 - 1 / sample.shape[0], sample.shape[0])
    x = x[sample > 0]
    sample = sample[sample > 0]
    sample = sample[x > 0]
    x = x[x > 0]
    m, c = minimize(lambda t: np.mean((np.log(sample) - (t[0] * np.log(-np.log(1 - x)) + t[1])) ** 2), [1, 0]).x
    return 1 / m, np.exp(-c - m)

def main():
    step = 4

    interarrivals = exponweib(size=10000)

    print(calculate_parameters(interarrivals))
    hours = []
    hour = []
    params = []
    time = 0
    last_time = 0
    for arrival in interarrivals:

        if time + arrival > last_time + 1000 * 60 * 60 * step:
            params.append(calculate_parameters(hour))
            hours.append(hour)
            hour = []
            last_time = time = last_time + 1000 * 60 * 60 * step


        time = time + arrival
        hour.append(arrival)

    fig, ax1 = plt.subplots()

    ax2 = plt.twinx()



    ax1.plot([p[0] for p in params])
    ax2.plot([p[1] for p in params], color='orange')
    plt.show()




if __name__ == '__main__':
    main()
