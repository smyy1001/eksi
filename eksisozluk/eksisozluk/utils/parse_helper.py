# parse_helper.py
import datetime
from eksisozluk.items import EksisozlukItem
from eksisozluk.utils.safe_get import ( safe_xpath_get, safe_xpath_string, )
import scrapy


class EksiSelectors:
    TOPIC_LIST = '//ul[@class="topic-list partial"]/li/a'
    ENTRY_LIST = '//li[@id="entry-item"]'
    
    KANAL_NAME = '//*[@id="left-index"]/h2/text()'
    
    # Account Info
    USERNAME = '@data-author'
    USER_PROFILE_URL = './/*[@id="entry-author"]/a/@href'
    AVATAR_URL = './/img[@class="avatar"]/@src'
    
    # Post Info
    CREATED_AT = './/a[@class="entry-date permalink"]/text()'
    POST_TITLE = '//h1[@id="title"]/@data-title'
    CONTENT = './/div[@class="content"]'
    
    # Pagination
    PAGER_CURRENT = '//div[@class="pager"]/@data-currentpage'
    PAGER_TOTAL = '//div[@class="pager"]/@data-pagecount'


def parse_entry(entry: scrapy.Selector, response: scrapy.http.Response):
    
    context = "parse_entry"
    item = EksisozlukItem()
    item["scraped_at"] = datetime.datetime.now().isoformat()
    item["source"] = "Ekşi Sözlük"
    kanal_name = safe_xpath_get(entry, EksiSelectors.KANAL_NAME, context=context)
    if kanal_name:
        item["kanal_name"] = kanal_name.replace("\n", "").replace("\r", "").replace("#", "").strip()

    # Kullanıcı bilgileri
    item["username"] = safe_xpath_get(entry, EksiSelectors.USERNAME, context=context)
    relative_url = safe_xpath_get(entry, EksiSelectors.USER_PROFILE_URL, context=context)
    if relative_url:
        item["account_url"] = response.urljoin(relative_url)
    item["avatar"] = safe_xpath_get(entry, EksiSelectors.AVATAR_URL, context=context)

    # Gönderi bilgileri
    item["title_url"] = response.url
    item["created_at"] = safe_xpath_get(entry, EksiSelectors.CREATED_AT, context=context)
    item["post_title"] = safe_xpath_get(response, EksiSelectors.POST_TITLE, context=context)

    content = safe_xpath_string(entry, EksiSelectors.CONTENT, context=context)
    if content:
        item["content"] = content.replace("\n", "").replace("\r", "").strip()

    return item
