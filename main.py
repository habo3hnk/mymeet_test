import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path
import os
import aiofiles
import logging
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://mymeet.ai/")
TEXT_DIR = Path("output/text")
IMG_DIR = Path("output/images")


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("MyMeetScraper")


class MyMeetScraper:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = None

        TEXT_DIR.mkdir(parents=True, exist_ok=True)
        IMG_DIR.mkdir(parents=True, exist_ok=True)

    async def fetch(self, url):
        logger.info(f"Fetching URL: {url}")
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    async def fetch_image(self, url, save_path):
        logger.info(f"Downloading image: {url}")
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                async with aiofiles.open(save_path, "wb") as f:
                    await f.write(await response.read())
            logger.info(f"Saved image to: {save_path}")
        except Exception as e:
            logger.warning(f"Failed to download image {url}: {e}")

    async def scrape(self):
        logger.info("Starting scraping process")
        async with aiohttp.ClientSession() as self.session:
            html = await self.fetch(self.base_url)
            soup = BeautifulSoup(html, "html.parser")
            await self.save_text(soup)
            await self.save_images(soup)
        logger.info("Scraping finished")

    async def save_text(self, soup):
        text = soup.get_text(separator="\n", strip=True)
        async with aiofiles.open(
            TEXT_DIR / "main_page.txt", "w", encoding="utf-8"
        ) as f:
            await f.write(text)
        logger.info(f"Text saved to {TEXT_DIR / 'main_page.txt'}")

    async def save_images(self, soup):
        tasks = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            img_url = urljoin(self.base_url, src)
            filename = os.path.basename(urlparse(img_url).path)
            if filename:
                save_path = IMG_DIR / filename
                tasks.append(self.fetch_image(img_url, save_path))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(MyMeetScraper().scrape())
