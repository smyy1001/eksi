import scrapy


class EksisozlukItem(scrapy.Item):
    scraped_at = scrapy.Field()
    source = scrapy.Field()
    kanal_name = scrapy.Field()
    
    # Account info
    username = scrapy.Field()
    account_url = scrapy.Field()
    avatar = scrapy.Field()
    
    # Post info
    title_url = scrapy.Field()
    created_at = scrapy.Field()
    post_title = scrapy.Field()
    content = scrapy.Field()
    
    pass