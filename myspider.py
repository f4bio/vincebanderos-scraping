import scrapy
import re
from urllib.parse import urlparse
from urllib.parse import parse_qs


class Geschichte(scrapy.Item):
    """
    Args:
            scrapy (_type_): _description_
    """
    id = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    url = scrapy.Field()
    paragraphs = scrapy.Field()


class EroSpider(scrapy.Spider):
    name = 'erogeschichtenspider'
    start_urls = [
        'https://www.erogeschichten.com/unreg/s/story.php?id=30000'
    ]


def clean_paragraphs(self, ps):
    paragraphs = []
    for p in ps:
        p = re.sub('\n*', '', p)
        p = re.sub('\r*', '', p)
        p = re.sub(' {2,}', ' ', p)
        paragraphs.append(p)
    paragraphs = list(filter(None, paragraphs))
    return paragraphs


def parse(self, response):
    self.logger.info('scraping from: %s', response.url)

    parsedUrl = urlparse(response.url)
    urlIdParam = parse_qs(parsedUrl.query)['id'][0]

    item = scrapy.Item()

    geschId = int(urlIdParam)
    author = response.xpath(
        '//span[@itemprop="author"]/span[@itemprop="name"]/text()').get()
    title = response.xpath('//h1/b[@itemprop="name"]/text()').get()
    summary = response.xpath(
        '//span[@itemprop="alternativeHeadline"]/text()').get()
    url = response.url

    firstParagraph = response.xpath(
        '//span[@itemprop="articleBody"]/text()').getall()
    followingParagraphs = response.xpath('//p/text()').getall()

    paragraphs = []
    paragraphs.extend(self.clean_paragraphs(firstParagraph))
    paragraphs.extend(self.clean_paragraphs(followingParagraphs))
    # self.logger.info('scraped & cleaned paragraphs %s', paragraphs)

    next_page_url = response.xpath(
        '//a[contains(@href, "rest=1")]/@href').get()
    if next_page_url is not None:
        url = response.urljoin(next_page_url)
        yield scrapy.Request(url, callback=self.parse_additional_page)

    yield {
        'id': geschId,
        'author': author,
        'title': title,
        'summary': summary,
        'url': url,
        'paragraphs': paragraphs
    }

def parse_additional_page(self, response):
    firstParagraph = response.xpath(
        '//span[@itemprop="articleBody"]/text()').get()
    followingParagraphs = response.xpath('//p/text()').getall()

    paragraphs = []
    paragraphs.extend(self.clean_paragraphs(firstParagraph))
    paragraphs.extend(self.clean_paragraphs(followingParagraphs))

    yield {
        "rest": paragraphs
    }
