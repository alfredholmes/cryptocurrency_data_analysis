#wss://stream.binance.com:9443/ws/btcusdt@depth
import os, time, asyncio
import websockets, requests
import json

def get_orderbook(symbol, limit=1000):
    orderbook = requests.get('https://www.binance.com/api/v1/depth?symbol=' + str(symbol) + '&limit=' + str(limit))
    if orderbook.status_code != 200:
        return None
    else:
        response = json.loads(orderbook.text)
        return response['lastUpdateId'], {float(price): float(quantity) for price, quantity in response['bids']}, {float(price): float(quantity) for price, quantity in response['asks']}

async def process(queue):
    while True:
        

async def main():

    last_id, bids, asks = get_orderbook('BTCUSDT', 5000)

    with open(str(last_id) + '_starting_orderbook.json', 'w') as jsonfile:
        json.dump({'bids': bids, 'asks': asks}, jsonfile)

    os.mkdir(str(last_id))
    i = 1
    cache = []


    async with websockets.connect('wss://stream.binance.com:9443/ws/btcusdt@depth@100ms') as ws:
        previous_time = time.time()

        while True:
             # TODO: Need to handle this not returning anything for a while
            print(time.time() - previous_time)
            try:
                process = await asyncio.wait_for(ws.recv(), 0.2 - (time.time() - previous_time))
                print('process')
            except asyncio.TimeoutError:
                print('timeout')
                break

            process = json.loads(process)

            bid_changes = {}
            ask_changes = {}
            for price, quantity in process['b']:
                if float(price) in bids:
                    bid_changes[float(price)] = float(quantity) - bids[float(price)]
                    if float(quantity) == 0:
                        bids.pop(float(price)) #to save memory, doesn't need to happen
                    else:
                        bids[float(price)] = float(quantity)
                else:
                    bid_changes[float(price)] = float(quantity)

            for price, quantity in process['a']:
                if float(price) in asks:
                    ask_changes[float(price)] = float(quantity) - asks[float(price)]
                    if float(quantity) == 0:
                        asks.pop(float(price))
                    else:
                        asks[float(price)] = float(quantity)
                else:
                    ask_changes[float(price)] = float(quantity)

            data = {'start_id': process['U'], 'end_id': process['u'], 'bid_changes': bid_changes, 'ask_changes': ask_changes}
            cache.append(data)
            if len(cache) >= 10: #write to file every minute
                with open(str(last_id) + '/' + str(i) + '.json', 'w') as jsonfile:
                    json.dump(cache, jsonfile)
                cache = []
                i += 1


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
