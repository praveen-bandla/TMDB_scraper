# TMDB_scraper

One of my favorite movies of all time is The Imitation Game!
The goal of this mini-project is to find movies/shows that share the most number of cast members with The Imitation Game. This was done by webscrapping the movie's TMDB webpage in order to extract the cast members, along with scrapping each cast member's TMDB webpage to obtain their featured titles. This project was for a class and its primary purpose was to get us accustomed to the basics of web-scrapping. The description of the project is written as a walk-through of the code required to generate the desired statistics.

<br>

### Part I: Web scrapping

<br>

We will create a `Spider` using the scrapy library to complete this task.

First, to create the scrapy project, we will run on our local terminal, upon activating the right environment, the following code:

```{python}
#scrapy startproject TMDB_scraper
```

Note that this will create a lot of files that will not be used. To create the spider, we will create a file called `tmdb_spider.py` inside the `spiders` directory of the project. We must create a class for our spider and will do so with the following code.

```{python}
import scrapy

class tmdbSpider(scrapy.Spider):
    name = '[insert custom name of spider]'

    start_urls = ['[insert list all tmdb movies/shows you want your spider to look at]']

    #for my file, I used start_urls = ['https://www.themoviedb.org/movie/205596-the-imitation-game']
```
<br>

Now, we need the following three functions to help us run our program:
1. `parse`
2. `parse_full_credits`
3. `parse_actor_page`

<br>

#### 1. `parse`

As can be seen in the docstring below, the goal of this function is to essentially obtain a scrapy request for the cast and crew redirect of the movie. In this case, we only had one starting url so the following implementation was used:

**NB**: `parse_full_credit` defined in the next section

```{python}
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
```

<br>

#### 2. `parse_full_credits`

From the cast and crew webpage, this function will obtain the url for each actor and create a new request using it.

Upon inspecting the source code of the cast and crew webpage, we can see that links to each of the actors' TMDB webpages are found here:

![Source code for the movie's cast and crew](https://user-images.githubusercontent.com/114946455/235502530-4667b7b8-e7b5-41d1-af2e-cf79fc1018f0.jpg)


**Note**: There is a known issue here: The same exact tags are used for the main cast and some of the crew members! Hence, some of the listed crew members will be listed and counted in our final results

We will use the tags as seen above to define the following function:

```{python}
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
        #specifically use div.info as there are two instances of the same link everywhere!
        all_links = response.css("ol.people.credits div.info a::attr(href)").getall()
                    
        #generating requests for each actor and calling the parse_actor_page function
        yield from (scrapy.Request("https://www.themoviedb.org" + url, callback=self.parse_actor_page) for url in all_links)

```
<br>

#### 3. `parse_actor_page`

For a given request, called on an actor's TMDB page, this function serves to extract all movies/shows where they have been credited. It first collects all the needed information, then saves it in a dictionary with the following code:

```{python}

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

```

We have now built our Spider! The only thing left is to run it. In our terminal, we do that with the following command

```{python}
#scrapy crawl tmdb_spider -o results.csv
```

The last part of the code outputs the results to the csv file.

In running this command, there is a good chance you will run into a `403 Error`! Refer to the following links to find a work-around:
1. [link1](https://doc.scrapy.org/en/latest/topics/practices.html#avoiding-getting-banned) 
2. [link2](https://scrapeops.io/python-scrapy-playbook/scrapy-403-unhandled-forbidden-error/)
3. [link3](https://scrapeops.io/web-scraping-playbook/403-forbidden-error-web-scraping/)
4. [link4](https://scrapingrobot.com/blog/most-common-user-agents/)


<br>
<br>


### Part II: Interpreting the results

Refer to the file `results.csv` to find the output of our spider. We will now briefly inspect the data to make an analysis!
Let us first take a look at the output

```{python}
#importing relevant libraries
import pandas as pd

df = pd.read_csv('results.csv')
df
```
<img width="619" alt="img1" src="https://user-images.githubusercontent.com/114946455/235503624-1086ad49-9d68-4935-b1a8-7ecc9ac01c15.png">

As we can see, we have every pairing of (actor, movie/show) stored in our dataframe. Since the goal of our task was to look at movies with the most overlapping actors as our chosen one, we will count the number of shared actors by each movie/show 

```{python}

#applying groupby and counting the number of entries (i.e, number of actors listed)
#resetting index to reframe the groupby output as a dataframe
df_analysis = df.groupby(['movie_or_TV_name']).agg('count').reset_index()

#sorting by most number of shared actors
df_analysis.sort_values(by = 'actor', ascending = False, inplace = True)

#for coherency
df_analysis.rename(columns = {"actor": 'Number of shared actors', 'movie_or_TV_name': 'Title'}, inplace = True)

#resetting index
df_analysis.reset_index(drop = True, inplace = True)

#starting from the second entry as the Imitation Game is a redundant entry
df_analysis = df_analysis[1:]

#outputting the results
df_analysis
```

<img width="613" alt="img2" src="https://user-images.githubusercontent.com/114946455/235503677-8c5cb36d-4537-4d3c-8258-32aef027a540.png">

Many of these titles would have only 1 or 2 shared actors. Let us take a look at only the titles with 3 or more shared actors

```{python}
df_analysis[df_analysis['Number of shared actors'] > 2]

```

<img width="608" alt="img3" src="https://user-images.githubusercontent.com/114946455/235503759-2f972e44-7052-4fd3-9dc4-02975680ebce.png">

<br>

Let us put this information into a simple visual using plotly! Here is a screenshot of the produced visual:

```{python}
import plotly.express as px
import numpy as np

#saving the output from the last cell
#we will have the hover information set to the movie name and leave the x-axis blank
df_analysis = df_analysis[df_analysis['Number of shared actors'] > 2]
fig = px.scatter(df_analysis, x = np.arange(1,17), y= 'Number of shared actors', 
                 hover_data=['Title'], color_discrete_sequence=['green'],
                 title = 'Movies/Shows with more than 2 shared actors with the Imitation Game')

#we do not need the ticks for the x-axis!
fig.update_xaxes(showticklabels = False)
#setting the x-axis title
fig.update_layout(xaxis_title = 'Movie/Show (hover to see name)')
fig.show()

```
<img width="629" alt="img4" src="https://user-images.githubusercontent.com/114946455/235503772-cc3d0c8b-cf67-4b29-b7fb-46f5634e2035.png">

And there we have it!

