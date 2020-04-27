# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from newspaper import Article
import re

class ToinewsSpider(scrapy.Spider):
    name = 'toiNews'
    allowed_domains = ['timesofindia.indiatimes.com']
    start_urls = ['https://timesofindia.indiatimes.com/india/']

    def parse(self, response):
        news_url = response.css("span.w_tle > a::attr(href)").extract() #extract all links from the TOI homepage
        news_title = response.css("span.w_tle > a::attr(title)").extract() #extract the title of all news article
        for url, title in zip(news_url, news_title):
            if('topic' in str(url) or 'photogallery' in str(url)): #links for a topic section and that leading to photogallery are skipped
                continue
            
            news = Article(url)
            try:
                news.download() #downloading the news article
                news.parse() #parsing the article
                news.nlp() #needed for finding keywords

            except:
                print("Failed to download") #exception handling for articles that could not be downloaded
                continue
            main_scraped_info = {
                'url' : url,
                'title' : title,
                'text' : news.text,
                'keywords' : news.keywords,
                'num_images' : len(news.images),
                'num_videos' : len(news.movies)
            }

            yield Request(url, callback=self.parse_newsarticle,meta={'parent_data': main_scraped_info})

    def parse_newsarticle(self, response):
        date = response.css("div._3Mkg-.byline::text").extract_first() 
        full_title = response.css("h1.K55Ut::text").extract_first() #the title used on the homepage is different from the original title of the article
        pattern = r'(\w{3}) (\d{2}), (\d{4})' #regex pattern for extracting the date
        date = re.search(pattern,date).group() #using regex to get the date the article was written/updated
        hrefs = response.css('a::attr(href)').extract() #getting all links in the article
        scraped_info = response.meta.get('parent_data') #getting the original metadata from scrapy
        scraped_info['date'] = date
        scraped_info['full_title'] = full_title
        scraped_info['num_hrefs'] = len(hrefs)
        yield scraped_info