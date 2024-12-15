import aiohttp


class AioSession:
    session: aiohttp.ClientSession = None

    def start(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def stop(self) -> None:
        if self.session is not None:
            await self.session.close()

HttpClientInstance = AioSession()
