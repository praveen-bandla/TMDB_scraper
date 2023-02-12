# to run 
# scrapy crawl tmdb_spider -o movies.csv

import scrapy

class TmdbSpider(scrapy.Spider):
    name = 'tmdb_spider'
    
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
        #all_links = response.css("ol[class=people credits] div[class=info] a::attr(href)").getall()
        all_links = response.css("ol.people.credits div.info a::attr(href)").getall()

        #filtering to only collect links of people
        actors = [link for link in all_links]
            
        # generating requests for each actor
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
        # extract names and titles
        actor_name = response.css("h2.title a::text").get()
        acting_credits = response.css("div.image img::attr(alt)").getall()

        # create a dict to store key-value pairs
        for title in acting_credits:
            yield { "actor" : actor_name, 
                "movie_or_TV_name" : title}
