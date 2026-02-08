import asyncio
import websockets
import json
import time


async def main():
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    async with websockets.connect(url) as ws:

        start = time.time()
        print("Connected to Binance trade stream.")

        async for message in ws:
            with open('stream_data.txt','a') as f:
                data = json.loads(message)
            #print(data)
                line = json.dumps(data)
                f.write(line+'\n')
                f.flush()

                if time.time() - start > 3:
                    break

asyncio.run(main())
