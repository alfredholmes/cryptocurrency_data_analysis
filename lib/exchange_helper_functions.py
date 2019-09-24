import exchange

import pandas as pd

def load_coinbase():
    ed = exchange.Exchange('coinbase.db')


    years = [i for i in range(2015, 2019)]

    csvs = []
    for year in years:
        csvs.extend(['../Download/Coinbase/' + str(year) + '/' + str(i) + '/BTC-USD.csv' for i in range(1, 13)])

    csvs.extend(['../Download/Coinbase/' + '2019/' + str(i) + '/BTC-USD.csv' for i in range(1, 8)])


    for csv in csvs:
        print(csv)
        df = pd.read_csv(csv)
        df['time'] = pd.to_datetime(df['time']).astype(int) / (10 ** 6)
        m = {'sell': False, 'buy': True}
        df['side'] = df['side'].map(m)
        df.columns = ['timestamp', 'trade_id', 'price', 'volume', 'maker']

        ed.write_transaction_dataframe('BTCUSDT', df)



    #ed.read_transactions_from_csv('BTCUSDT', csvs)

def load_binance():
    csvs = []
    for year in years:
        csvs.extend(['../Download/Coinbase/' + str(year) + '/' + str(i) + '/BTCUSDT.csv' for i in range(1, 13)])

    csvs.extend(['../Download/Coinbase/' + '2019/' + str(i) + '/BTCUSDT.csv' for i in range(1, 8)])


    ed.read_transactions_from_csv('BTSUSDT', csvs)


if __name__ == '__main__':
    load_coinbase()
    load_binance()
