import pandas as pd, sqlite3
import numpy as np



class Exchange:
    def __init__(self, database_location, name='exchange'):
        self.database = sqlite3.connect(database_location)
        self.cur = self.database.cursor()
        self.name = name


    def read_transactions_from_csv(self, pair, csvs):
        for csv in csvs:
            transactions = pd.read_csv(csv)
            transactions.to_sql(name=pair + '_transactions', con=self.database, if_exists='append', index='False')
            #todo handle the failing of the database to be able to add new files

        #then process the loaded orders and insert the orders into the database
        #An order is just a collection of transactions

    def write_transaction_dataframe(self, pair, df):
        df.to_sql(name=pair + '_transactions', con=self.database, if_exists='append', index='False')

    def get_transaction_iterator(self, pair):
        return self.cur.execute('SELECT * FROM ' + pair + '_transactions')


    def get_orders(self, pair, start_time=0, end_time=np.inf):
        # TODO: Cache this in the database

        if end_time == np.inf:
            it = self.cur.execute('SELECT timestamp, price, volume, maker FROM ' + pair + '_transactions WHERE timestamp >= ? ORDER BY timestamp ASC', (start_time,))
        else:
            it = self.cur.execute('SELECT timestamp, price, volume, maker FROM ' + pair + '_transactions WHERE timestamp >= ? AND timestamp < ? ORDER BY timestamp ASC', (start_time, end_time))

        previous_transaction = None

        return OrderIterator(it)


    def get_total_orders_ts(self, pair, tick=1000 * 60, start_time=0, end_time=np.inf):
        orders = self.get_orders(pair, start_time, end_time)

        number_of_orders = []
        current_time = None
        current_orders = [0, 0]

        prices = []

        for order in orders:
            if current_time is None:
                current_time = order.time

            if current_time + tick < order.time:
                steps = int(np.floor((order.time - current_time) / tick))
                number_of_orders.extend([current_orders] + [[0, 0]] * (steps - 1))
                prices.extend([order.average_price] * steps)


                current_orders = [0, 0]
                current_time += steps * tick


            current_orders[order.buyer] += 1

        return number_of_orders, prices




class Order:
    #Market order class
    def __init__(self, time, buyer, volume, start_price, end_price, average_price):
        self.time = time
        self.buyer = buyer
        self.volume = volume
        self.start_price = start_price
        self.end_price = end_price
        self.average_price = average_price


class OrderIterator:
    def __init__(self, transaction_iterator):
        self.it = transaction_iterator
        self.to_process = []

    def __iter__(self):
        return self


    def __next__(self):
        #load all the next orders that occur at the same time and process them to catch multiple buy / sell orders in the
        #market orders that move the price
        if len(self.to_process) == 0:
            time = None
            for transaction in self.it:
                if time is None:
                    time = transaction[0]
                    self.to_process.append(transaction)
                elif time == transaction[0]:
                    self.to_process.append(transaction)
                else:
                    break


        if len(self.to_process) == 0:
            raise StopIteration

        time = self.to_process[0][0]
        buyer = self.to_process[0][3]
        start_price = self.to_process[0][1]
        volume = 0
        base = 0

        processed = set()

        for i, transaction in enumerate(self.to_process):

            if transaction[3] == buyer:
                volume += transaction[2]
                base += transaction[1] * transaction[2]
                end_price = transaction[1]
                processed.add(i)

        self.to_process = [t for i, t in enumerate(self.to_process) if i not in processed]

        return Order(time, not buyer, volume, start_price, end_price, base / volume)










#end of the file
