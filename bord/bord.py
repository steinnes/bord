import asyncio
import time

from pyppeteer import launch

from bord.config import Config, Screen


class Tab:
    def __init__(self, tab, screen: Screen):
        self.tab = tab
        self.screen = screen
        self._last_load = None

    async def load(self, width: int, height: int):
        await self.tab.setViewport(dict(width=width, height=height))
        await self.tab.goto(self.screen.url, timeout=0)
        self._last_load = time.time()

    async def display(self):
        print("Displaying: ", self.screen)
        if self.screen.refresh_interval is not None:
            if self._last_load < (time.time() - self.screen.refresh_interval):
                print("Reloading: ", self.screen)
                await self.tab.reload()
                self._last_load = time.time()

        await self.tab.bringToFront()
        await asyncio.sleep(self.screen.display_time)


class Bord:
    def __init__(self, config: Config):
        self.config = config
        self.tabs = []

    async def start(self):
        browser_kwargs = dict(
            headless=False,
            dumpio=True,
            logLevel="INFO",
            autoclose=False,
            args=["--kiosk", "--disable-infobars"],
            ignoreDefaultArgs=["--enable-automation"],
        )
        if self.config.executable_path is not None:
            browser_kwargs["executablePath"] = self.config.executable_path

        self.browser = await launch(**browser_kwargs)
        await self.init_tabs()
        for tab in self.tabs:
            await tab.load(width=self.config.monitor.width, height=self.config.monitor.height)

        while True:
            await self.rotate()

    async def init_tabs(self):
        tabs = await self.browser.pages()
        while len(tabs) < len(self.config.screens):
            tabs.append(await self.browser.newPage())

        for tab, screen in zip(tabs, self.config.screens):
            self.tabs.append(Tab(tab, screen))

    async def rotate(self):
        for tab in self.tabs:
            await tab.display()
