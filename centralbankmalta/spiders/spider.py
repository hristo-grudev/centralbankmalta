import scrapy

from scrapy.loader import ItemLoader
from ..items import CentralbankmaltaItem
from itemloaders.processors import TakeFirst


class CentralbankmaltaSpider(scrapy.Spider):
	name = 'centralbankmalta'
	start_urls = ['https://www.centralbankmalta.org/en/news/14']

	def parse(self, response):
		years_links = response.xpath('//ul[@class="news_cat"]/li/a/@href').getall()
		yield from response.follow_all(years_links, self.parse_year)

	def parse_year(self, response):
		post_links = response.xpath('//div[@class="button"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@class="pagination"]//a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		if 'file' in response.url:
			return
		title = response.xpath('//h2/text()').get()
		description = response.xpath('//div[@class="content"]//text()[normalize-space() and not(ancestor::h1 | ancestor::h2 | ancestor::span[@class="date"] | ancestor::div[@class="breadcrumbs"])]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//span[@class="date"]/text()').get()

		item = ItemLoader(item=CentralbankmaltaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
