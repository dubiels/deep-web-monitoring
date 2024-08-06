import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import time

class WebScraper:
    def __init__(self, urls, keywords, max_concurrent_requests=10):
        self.urls = urls
        self.keywords = keywords
        self.max_concurrent_requests = max_concurrent_requests

    async def fetch(self, browser, url):
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})
        content = await page.content()
        await page.close()
        return content

    async def fetch_all(self):
        browser = await launch(headless=True)
        tasks = []
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        for url in self.urls:
            task = asyncio.ensure_future(self.bounded_fetch(semaphore, browser, url))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        await browser.close()
        return results

    async def bounded_fetch(self, semaphore, browser, url):
        async with semaphore:
            try:
                response = await self.fetch(browser, url)
                return url, response
            except Exception as e:
                return url, str(e)

    def scrape(self):
        loop = asyncio.get_event_loop()
        html_contents = loop.run_until_complete(self.fetch_all())
        results = []
        for url, content in html_contents:
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text()
                for keyword in self.keywords:
                    if keyword.lower() in text.lower():
                        results.append((url, keyword))
                        break
        return results

if __name__ == "__main__":
    urls = [
        "https://quotes.toscrape.com/",
        "https://books.toscrape.com/"
    ]
    keywords = ["happiness"]

    scraper = WebScraper(urls, keywords)
    start_time = time.time()
    results = scraper.scrape()
    end_time = time.time()

    for url, keyword in results:
        print(f"Keyword '{keyword}' found in URL: {url}")
    
    print(f"Time taken: {end_time - start_time} seconds")
