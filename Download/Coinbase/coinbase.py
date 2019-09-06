import requests
import json

import csv
import time
import os
import datetime


def save_progress(line):
    with open('progress.coinbase', 'w') as file:
        file.write(str(line))

def get_progress():
    try:
        with open('progress.coinbase', 'r') as file:
            progress = file.readline()
            return int(progress)
    except FileNotFoundError:
        return 0

def get_orders(start):
    #https://api.pro.coinbase.com/products/BTC-USD/trades?after=10000
    #max number of returns is 100, so need to request 100 orders after (as the book is reversed) start
    r = requests.get('https://api.pro.coinbase.com/products/BTC-USD/trades?after=' + str(start + 100))
    return [x for x in reversed(json.loads(r.text))]

def write_orders(orders, year, month, symbol):
    try:
        os.mkdir(str(year) + '/' + str(month))
    except FileExistsError:
        pass
    except FileNotFoundError:
        os.mkdir(str(year))
        os.mkdir(str(year) + '/' + str(month))

    with open(str(year) + '/' + str(month) +'/' + symbol + '.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, ['time', 'trade_id', 'price', 'size', 'side'])
        writer.writeheader()
        for order in orders:
            writer.writerow(order)



def main():
    symbol = 'BTC-USD'

    #time per request is 1 / 3 seconds
    request_time = 1 / 3
    #get the last trade:
    r = requests.get('https://api.pro.coinbase.com/products/' + symbol + '/trades')
    last_id = int(json.loads(r.text)[0]['trade_id'])

    start = get_progress()
    time.sleep(request_time)

    orders = []

    previous_date = None

    for i in range(start, last_id, 100):
        previous_time = time.time()
        current_orders = get_orders(i)


        last_order = current_orders[-1]
        date = datetime.datetime.strptime(last_order['time'], '%Y-%m-%dT%H:%M:%S.%fZ')

        if previous_date is None:
            previous_date = date

        if date.month != previous_date.month:

            print('Writing month', previous_date.month, previous_date.year)

            #find first order of the month
            for j, o in enumerate(current_orders):
                date = datetime.datetime.strptime(o['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                if date.month != previous_date.month:
                    break

            write_orders(orders, previous_date.year, previous_date.month, symbol)


            orders.extend(current_orders[:j])
            orders = current_orders[j:]
            previous_date = date
            save_progress(i + j)

        else:
            orders.extend(current_orders)


        if time.time() - previous_time < request_time:
            try:
                time.sleep(request_time - (time.time() - previous_time))
            except ValueError:
                pass

if __name__ == '__main__':
    main()
