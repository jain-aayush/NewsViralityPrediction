# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from newspaper import Article
import csv 
import re

class ToinewsSpider(scrapy.Spider):
    name = 'toiNews'
    allowed_domains = ['timesofindia.indiatimes.com']
    start_urls = ['https://timesofindia.indiatimes.com/india/']

    def parse(self, response):
        news_url = response.css("span.w_tle > a::attr(href)").extract()
        news_title = response.css("span.w_tle > a::attr(title)").extract()
        for url, title in zip(news_url[:5], news_title[:5]):
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

                main_scraped_info = {
                    'url' : url,
                    'title' : title,
                    'text' : news.text,
                    'keywords' : news.keywords
                }

                yield Request(url, callback=self.parse_newsarticle,meta={'parent_data': main_scraped_info})

    def parse_newsarticle(self, response):
        date = response.css("div._3Mkg-.byline::text").extract_first()
        full_title = response.css("h1.K55Ut::text").extract_first()
        pattern = r'(\w{3}) (\d{2}), (\d{4})'
        date = re.search(pattern,date).group()
        scraped_info = response.meta.get('parent_data')
        scraped_info['date'] = date
        scraped_info['full_title'] = full_title
        yield scraped_info