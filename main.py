from bot_f import start , periodic_parse_results
import asyncio

if __name__=='__main__':
    loop = asyncio.get_event_loop()
    tasks = [start(), periodic_parse_results()]
    loop.run_until_complete(asyncio.gather(*tasks))

