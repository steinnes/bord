import asyncio
import json

from pyppeteer import launch
from typing import List

from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    interval: int
    urls: List[str]


def read_config():
    with open("./config.json") as fp:
        cfg_json = json.load(fp)
    return Config(**cfg_json)



async def main():
    browser = await launch(executablePath='/usr/bin/chromium-browser', headless=False, dumpio=True, logLevel="INFO", autoclose=False)
    config = read_config()
    tabs = await browser.pages()
    while len(tabs) < len(config.urls):
        tabs.append(await browser.newPage())

    for tab, url in zip(tabs, config.urls):
        print("Set tab:", tab, " to url:", url)
        await tab.goto(url, timeout=0)

    tab_index = 0
    import time
    while True:
        tab = tabs[tab_index]
        await asyncio.sleep(config.interval)
        print(time.ctime())
        print(f"Will show tab[{tab_index}] = {tab}")
        print("..isClosed=", tab.isClosed())
        await tabs[tab_index].bringToFront()
        tab_index += 1
        if tab_index == len(tabs):
            tab_index = 0


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
