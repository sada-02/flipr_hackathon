import asyncio
from playwright.async_api import async_playwright

URL = "https://www.tribuneindia.com/topic"
async def tribune_topic_scraper(url: str = URL, topics: list = [], max_articles: int = 5) -> list:

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        links = []
        print("🔍 Searching for topic based news on Tribune India")

        for topic in topics:
            print(f"🔍 Searching for: {topic}")
            topic = topic.lower().replace(" ", "-")
            try:
                await page.goto(f"{url}/{topic}/", timeout=20000)  # 60 sec timeout

                # Wait for elements to load
                await page.wait_for_selector("div.post-item.search_post", timeout=10000)

                # Extract all links
                topic_links = await page.eval_on_selector_all(
                    "div.post-featured-img-wrapper a",  # Target elements
                    "elements => elements.map(el => el.href)"
                )
                topic_links = topic_links[:min(max_articles, len(topic_links))]
                links.append((topic_links, topic))
                
            except Exception as e:
                print(f"Error: {e}")
                continue

        news = []
        for topic_links, topic in links:
            for url in topic_links:
                try:
                    await page.goto(url, timeout=20000)

                    h1_text = await page.text_content('h1.post-header')

                    p_elements = await page.query_selector_all('div#story-detail p')
                    p_texts_content = [await p.text_content() for p in p_elements]
                    article = ' '.join(p_texts_content)

                    published_time = await page.text_content('div.timesTamp span.updated_time')
                    
                    news.append({"title": h1_text, "date_time": published_time, "content": article})
                    
                except Exception as e:
                    print(f"Error: {e}")
                    continue

        # Close the browser
        await browser.close()
        
        print("Scraping complete. Total articles scraped:", len(news))
        return news
