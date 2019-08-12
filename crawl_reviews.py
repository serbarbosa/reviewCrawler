import os

def run_crawler(search):

    os.system('scrapy crawl %s %s %s %s %s %s %s' % ('buscape_crawler', '-s', 'HTTPCASH_ENABLED=1', '-o', 'reviews.csv', '-a', 'search="'+search+'"'))
    #pool = Pool(processes=len(spider_names))
    #pool.map(_crawl, spider_names


if __name__ == "__main__":
    
    run_crawler('buscape ative')
    
    
    
    
