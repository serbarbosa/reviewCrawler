'''
                    Problemas por tratar
Algumas paginas do buscape retornam conteudo duplicado outras nao.
Consequentemente necessita-se detectar quando isso acontece.
Foi feita a deteccao para paginas completas(5 revisoes), porem
na ultima pagina de revisao, quando existirem ate duas revioes,
a deteccao nao pode ser feita e serao extraidas revisoes repetidas (
ate 2 repeticoes no pior caso).
O problema podera ser facilmente resolvido na versao 1.7 do Scrapy
'''

import scrapy
import sys
sys.path.insert(1,'../utils')
import utils
import math

class BuscapeReviewSpider(scrapy.Spider):
    
    name = 'buscape_crawler'
    
    def __init__(self, search):
        buscape_url = 'https://www.buscape.com.br'
        #comeca acessando url correspondente a busca solicitada
        self.start_urls = [buscape_url + '/search/' + search.replace(' ', '-') + 
                    '?fromSearchBox=true&produto=' + search.replace(' ', '+')+'/']
        self.review_counter = 1
        self.review_amnt = 0
        self.per_page = 10       #numero de revisoes mostradas por pagina do buscape
        self.first_page = 5

    def parse(self, response):
        ''' Recupera o href para o primeiro produto da busca. '''
        
        first_product = response.css('.inner a::attr(href)').get()
            #vamos agora acessar a pagina do produto
        yield scrapy.Request(
            response.urljoin(first_product),
            callback=self.parse_product
        )

    def parse_product(self, response):
        ''' Verifica o nmr de revisoes do produto. E decide baseado na qtd de revisoes
        como sera feita a extracao. '''

        has_review = response.css('.product-rating__rating-count::text').getall()
        self.review_amnt = 0 if len(has_review) == 0 else int(has_review[1])
        #agora recuperamos as revisoes da primeira pagina do produto
        reviews = response.css('.consumer-content')
        
        if(self.review_amnt <= self.first_page) :
            #o site mostra 5 revisoes na primeira pagina. so sera usada se o total for 5 ou menos
            limit = self.per_page if self.review_amnt > self.per_page else self.review_amnt

            #extraindo revisoes da primeira pagina
            for i in range(limit):
                 
                date = reviews[i].css('.consumer-login--lastAcess::text').get().split()[1]
                stars = len(reviews[i].css('.starfull').getall())
                recommended = reviews[i].xpath('./div//div//span//span/text()').getall()[1]
                title = reviews[i].xpath('./div//div//span[has-class("body--big consumer-description__title")]/text()').get()
                review_body = reviews[i].css('p.consumer-description__txt::text').get()
                
                with open('reviewsFiles/' + str(self.review_counter) + '.txt', 'w') as rev:
                    #review_body_ascii = utils.find_equivalent_char(review_body)  ---sera tratado depois qndo necessario
                    rev.write(review_body + '\n')
                    self.review_counter += 1

                yield{
                    'data' : date,
                    'estrelas' : stars,
                    'foi_recomendado' : recommended + ' este produto', #para padronizar a saida
                    'titulo' : title,
                    'revisao' : review_body
                }
            
            '''#vai buscar link para o restante das revisoes
            if(self.review_amnt > self.per_page):
                more_reviews = response.css('a.button-tab-links::attr(href)').get()
                
                yield scrapy.Request(
                    response.urljoin(more_reviews),
                    callback=self.parse_reviews
                    #,cb_kwargs=dict(is_duplicated=False) usar qndo atualiar para versao 1.7 para resolver bug
                )'''
        else:
            reviews_page = response.css('a.button-tab-links::attr(href)').get()
            num_pages = math.ceil(self.review_amnt/self.per_page) 
            
            for i in range(1, num_pages + 1):
                yield scrapy.Request(
                    response.urljoin(reviews_page)+'?page='+str(i),
                    callback=self.parse_reviews
                )

            
    def parse_reviews(self, response):
        ''' Extrai as revisoes de uma pagina. '''
        
        #seleciona as reviews da pagina.
        reviews = response.css('.review-list__item')
        
        for i in range(len(reviews)):
            
            try:
                date = reviews[i].css('.review-list__created-at::text').get()
                stars = len(reviews[i].css('.review-stars__star-count'))
                recommended = reviews[i].css('p::text').get()
                title = reviews[i].css('.review-list__body h3::text').get()
                review_body = '\n'.join(reviews[i].css('.review-list__body p::text').getall())       
                
                with open('reviewsFiles/' + str(self.review_counter) + '.txt', 'w') as rev:
                    #review_body_ascii = utils.find_equivalent_char(review_body) --- sera tratado depois se necessario 
                    rev.write(review_body + '\n')
                    self.review_counter += 1

                yield{
                    'data' : date,
                    'estrelas' : stars,
                    'foi_recomendado' : recommended,
                    'titulo' : title,
                    'revisao' : review_body
                }
            
            except IndexError:
                pass

