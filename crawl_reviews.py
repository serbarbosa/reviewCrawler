from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os

def run_crawler(product):
    #seguindo a documentacao do scrapy ('run Scrapy from a script')
    
    csv_filename = 'reviews.csv'
    
    #deleta arquivo csv se esse ja existir
    try:
        os.remove(csv_filename)
    except OSError:
        pass

    #personalizando configuracoes
    settings = get_project_settings()
    settings.set('LOG_ENABLED', False)
    settings.set('FEED_FORMAT', 'csv')
    settings.set('FEED_URI', 'reviews.csv')
    settings.set('ROBOTSTXT_OBEY', False)

    process = CrawlerProcess(settings)
    process.crawl('buscape_crawler', search=product)
    process.start()
    #os.system('scrapy crawl %s %s %s %s %s %s %s' % ('buscape_crawler', '-s', 'HTTPCASH_ENABLED=1', '-o', 'reviews.csv', '-a', 'search="'+search+'"'))


if __name__ == "__main__":
    
    run_crawler('brastemp ative')
    
    
    
    
