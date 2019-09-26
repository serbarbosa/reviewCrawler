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
import sys, os
sys.path.insert(1,'../utils')
import utils

class BuscapeReviewSpider(scrapy.Spider):
    
    name = 'buscape_crawler_deprecated'
    
    def __init__(self, search):
        buscape_url = 'https://www.buscape.com.br'
        #comeca acessando url correspondente a busca solicitada
        self.start_urls = [buscape_url + '/search/' + search.replace(' ', '-') + 
                    '?fromSearchBox=true&produto=' + search.replace(' ', '+')+'/']
        self.review_counter = 1
        self.review_amnt = 0
        self.per_page = 5       #numero de revisoes mostradas por pagina do buscape

    def parse(self, response):
        #recupera o href para o primeiro produto da busca
        first_product = response.css('.inner a::attr(href)').get()
        
        #vamos agora acessar a pagina do produto
        yield scrapy.Request(
            response.urljoin(first_product),
            callback=self.parse_product
        )

    def parse_product(self, response):
        #primeiro verifica-se quantas revisoes tem o produto
        has_review = response.css('.product-rating__rating-count::text').getall()
        self.review_amnt = 0 if len(has_review) == 0 else int(has_review[1])
        
        #agora recuperamos as revisoes da primeira pagina do produto
        reviews = response.css('.consumer-content')
       
        #o suite mostra 5 revisoes por pagina
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
        
        #vai buscar link para o restante das revisoes
        if(self.review_amnt > self.per_page):
            more_reviews = response.css('a.button-tab-links::attr(href)').get()
            
            yield scrapy.Request(
                response.urljoin(more_reviews),
                callback=self.parse_reviews
                #,cb_kwargs=dict(is_duplicated=False) usar qndo atualiar para versao 1.7 para resolver bug
            )
            
    def parse_reviews(self, response):
        
        #seleciona as reviews da pagina.
        #Vai pegar duplicado, logo sera analisado metade do resultado apenas
        reviews = response.css('.review div[itemprop="review"] div.row div.small-10')
        pagerev_amnt = 0
        is_duplicated = False   #informa se a pagina web esta com conteudo duplicado ou nao
        
        #--- bug de dados duplicados na pagina 
        #--- nao resolve o bug, apenas diminui um pouco o impacto
        if(self.review_amnt - self.review_counter <= self.per_page):
            #checa se esta na ultima pagina. Vai pegar o que sobra
            pagerev_amnt = self.review_amnt - self.review_counter + 1
        else:
            #precisa pegar 5 revisoes, pois nao eh a ultima pagina
            pagerev_amnt = self.per_page
        
        
        #aqui checa se foram retornados mais resultados do que o previsto
        #indicando que foram armazenados em duplicata
        if(len(reviews) > pagerev_amnt):
            is_duplicated = True
        
        for i in range(pagerev_amnt):
            
            try:
                date = reviews[i].css('div time::text').get()
                stars = len(reviews[i].css('.starfull'))
                recommended = reviews[i].css('div span.review-meta__recommend::text').get()
                title = reviews[i].css('div h4 a::text').get()
                review_body = '\n'.join(reviews[i].css('div p::text').getall())       
                
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
                #excessao causada pelo bug ainda nao tratado. (aguardando versao 1.7 do scrapy)
                pass

        #agora faz-se o mesmo para as revisoes em todas as paginas
        
        #tambem retorna a lista dobrada
        links = response.css('.pages-list li a.item')   
        
        link_amnt = len(links)//2 if(is_duplicated) else len(links)
        
        for i in range(link_amnt):
            
            try:
                if( int(links[i].css('::text').get()) > 1):

                    yield scrapy.Request(
                        links[i].css('::attr(href)').get(),
                        callback=self.parse_reviews
                    )
            except ValueError:
                #entrou na tab de proxima pagina ou anterior
                pass 
