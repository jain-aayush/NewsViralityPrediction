# -*- coding: utf-8 -*-
import scrapy
from newspaper import Article

class ToinewsSpider(scrapy.Spider):
    name = 'toiNews'
    allowed_domains = ['https://timesofindia.indiatimes.com/india']
    start_urls = ['https://timesofindia.indiatimes.com/india/']

    def parse(self, response):
        news_url = response.css("span.w_tle > a::attr(href)").extract()
        news_title = response.css("span.w_tle > a::attr(title)").extract()
        for url, title in zip(news_url, news_title):
            if('topic' in str(url)):
                continue
            if(str(url).startswith('http')):
                news = Article(url)
                try:
                    news.download()
                except:
                    print("Failed to download")
                    continue
                news.parse()
                news.nlp()

                scraped_info = {
                    'url' : url,
                    'title' : title,
                    'text' : news.text,
                    'keywords' : news.keywords
                }
                yield scraped_info