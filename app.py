import asyncio
import json

from pyppeteer import launch
from typing import List

from dataclasses import dataclass

from screeninfo import get_monitors, Enumerator, Monitor


@dataclass(frozen=True)
class Config:
    interval: int
    urls: List[str]
    monitor: Monitor


def init_config():
    with open("./config.json") as fp:
        cfg_json = json.load(fp)

    monitors = [monitor for monitor in get_monitors(Enumerator.Xinerama)]
    assert len(monitors) == 1, "Multiple monitors are not supported"
    return Config(monitor=monitors[0], **cfg_json)


async def main():
    browser = await launch(
        headless=False, dumpio=True, logLevel="INFO", autoclose=False, args=['--kiosk', '--disable-infobars'],
    )
    config = init_config()
    tabs = await browser.pages()
    while len(tabs) < len(config.urls):
        tabs.append(await browser.newPage())

    for tab, url in zip(tabs, config.urls):
        print("Set tab:", tab, " to url:", url)
        await tab.setViewport(dict(width=config.monitor.width, height=config.monitor.height))
        await tab.goto(url, timeout=0)

    tab_index = 0

    while True:
        tab = tabs[tab_index]
        await asyncio.sleep(config.interval)
        print(f"Switching to tab[{tab_index}] = {tab}")
        await tabs[tab_index].bringToFront()
        tab_index += 1
        if tab_index == len(tabs):
            tab_index = 0


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
