# to run 
# scrapy crawl tmdb_spider -o movies.csv

import scrapy

class TmdbSpider(scrapy.Spider):
    name = 'tmdb_spider'
    
    #the base url to start from
    start_urls = ['https://www.themoviedb.org/movie/205596-the-imitation-game']
    
    def parse(self, response):
        '''
        For a given TMDB movie/show, yields a scrapy request for 
        the cast and crew by calling parse_full_credits

        inputs:
        self: (TmdbSpider Object)
        response: stores the request response in this variable

        no output
        '''
        #cast and crew page
        cast_and_crew = self.start_urls[0]+ "/cast"
        #Call the parse full credit function on the cast_and_crew webpage
        yield scrapy.Request(cast_and_crew, callback=self.parse_full_credits)

    def parse_full_credits(self, response):
        '''
        For a given TMDB movie/show's cast and crew page, yields a
        request for each actor listed

        inputs:
        self: (TmdbSpider Object)
        response: stores the request response in this variable

        no output
        '''
        #collecting links in the html code of <ol class="people credits">
        all_links = response.css("ol.people.credits div.info a::attr(href)").getall()
                    
        #generating requests for each actor and calling the parse_actor_page function
        yield from (scrapy.Request("https://www.themoviedb.org" + url, callback=self.parse_actor_page) for url in actors)

    def parse_actor_page(self, response):
        '''
        For a given actor url, yields a dict containing their name
        and all acting credits 

        inputs:
        self: (TmdbSpider Object)
        response: stores the request response in this variable

        no output
        '''
        #extracting names and titles from the page
        actor_name = response.css("h2.title a::text").get()
        acting_credits = response.css("div.image img::attr(alt)").getall()

        #creating a dict to store the ouput as key-value
        for title in acting_credits:
            yield { "actor" : actor_name, 
                "movie_or_TV_name" : title}
