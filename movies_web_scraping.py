"""
Predicting Movie Revenue --
Functions for web scraping
Functions are imported and executed in the __main__.py file
"""

import pandas as pd
import numpy as np
import time
import random
import pickle
import sys
from warnings import warn
from requests import get
from bs4 import BeautifulSoup

#====================================================================
### Scraper for IMDB
#====================================================================

def imdb_scraper():
    """
    Scrapes movie data from IMDB then saves as pickled dataframe
    """
    names = []
    years = []
    imdb_ratings = []
    metascores = []
    votes = []
    runtimes = []
    certificates = []
    genres = []
    directors = []
    stars = []

    start_time = time.time()
    requests = 0

    pages = [str(i) for i in range(1, 139)] #138 pages 

    for page in pages:

        # make a get request
        response = get('https://www.imdb.com/search/keyword/?mode=advanced&page=' + page +  
                '&ref_=kw_nxt&title_type=movie&release_date=1989%2C2019&sort=year,asc&num_votes=10000%2C')
        
        # pause the loop
        time.sleep(random.randint(2,8))

        # monitor the requests
        requests += 1
        elapsed_time = time.time() - start_time
        print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        clear_output(wait = True)

        # throw a warning for non-200 status codes
        if response.status_code != 200:
            warn('Request: {}; Status code: {}'.format(requests, response.status_code))

        # break the loop if the number of requests is greater than expected
        if requests > 200:
            warn('Number of requests was greater than expected.')
            break

        # parse the content of the request with beautifulsoup
        soup = BeautifulSoup(response.text, 'lxml') # html.parser

        # select all the 50 movie containers from a single page
        movie_containers = soup.find_all('div', class_ = 'lister-item mode-advanced')

        # for every movie of these 50
        for container in movie_containers:
            # if the movie has a metascore, then:
            # if container.find('div', class_ = 'ratings-metascore') is not None:

            # scrape the name
            name = container.h3.a.text
            names.append(name)

            # scrape the year
            year = container.h3.find('span', class_ = 'lister-item-year').text
            years.append(year)

            # scrape the imdb rating
            imdb = container.strong
            if imdb:
                imdb_ratings.append(float(imdb.text))
            else:
                imdb = 'no stars given'
                imdb_ratings.append(imdb)

            # scrape the metascore
            m_score = container.find('span', class_ = 'metascore')
            if m_score:
                metascores.append(int(m_score.text))
            else:
                m_score = 'no metascore'
                metascores.append(m_score)

            # scrape the number of votes
            vote = container.find('span', attrs = {'name':'nv'})
            if vote:
                vote = vote['data-value']
                votes.append(int(vote))
            else:
                vote = 'no votes'
                votes.append(vote)

            # scrape the runtime
            runtime = container.find('p', class_='text-muted').find('span', class_='runtime')
            if runtime:
                runtimes.append(runtime.text)
            else:
                runtime = 'no runtime'
                runtimes.append(runtime)

            # scrape the certificate            
            certificate = container.find('p', class_='text-muted').find('span', class_='certificate')
            if certificate:
                certificates.append(certificate.text)
            else:
                certificate = 'not rated'
                certificates.append(certificate)

            # scrape the genre
            genre = container.find('p', class_='text-muted').find('span', class_='genre')
            if genre:
                genres.append(genre.text.split())
            else:
                genre = 'no genre'
                genres.append(genre)

            # scrape the name of the director
            director = container.find('div', class_='lister-item-content').find('p', class_="").a # picks up only one director
            if director:
                directors.append(director.text)
            else:
                director = 'no director'
                directors.append(director)

            # scrape the names of the stars
            star = container.find('div', class_='lister-item-content').find('p', class_="").find_all('a') # may pick up any co-directors
            if star:
                star = star[1:]
                star = [a.text for a in star]   
                stars.append(star)
            else:            
                star = 'no stars'
                stars.append(star)                                    
            
    print((time.time()-start_time)/60, "minutes")

    # store lists into dataframe
    imdb_data = pd.DataFrame({'movie': names,
    'year': years,
    'imdb': imdb_ratings,
    'metascore': metascores,
    'votes': votes,
    'runtime': runtimes,
    'certificate': certificates,
    'genre': genres,                          
    'director': directors,
    'stars': stars                    
    })

    return imdb_data

#====================================================================
### Scraper for the-numbers
#====================================================================

def thenumbers_scraper():
    """
    Scrapes movie data from IMDB then saves as pickled dataframe
    """
    movie_names = []
    release_dates = []
    production_budgets = []
    domestic_grosses = []
    worldwide_grosses = []

    start_time = time.time()
    requests = 0

    pages = ['/' + str(i) for i in np.arange(101, 6002, 100)] # 61 pages of results
    pages.insert(0, "") # insert "" in front of list

    for page in pages:

        # make a get request
        url = 'https://www.the-numbers.com/movie/budgets/all'
        response = get(url + page)
        
        # pause the loop
        time.sleep(random.randint(2,8))

        # monitor the requests
        requests += 1
        elapsed_time = time.time() - start_time
        print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        clear_output(wait = True)

        # throw a warning for non-200 status codes
        if response.status_code != 200:
            warn('Request: {}; Status code: {}'.format(requests, response.status_code))

        # break the loop if the number of requests is greater than expected
        if requests > 200:
            warn('Number of requests was greater than expected.')
            break

        # parse the content of the request with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml') 
        movie_table = soup.find('table')
        rows = [row for row in movie_table.find_all('tr')]
        
        for row in rows[1:101]:
            
            items = row.find_all('td')

            # scrape the release date
            release_date = items[1].find('a')
            if release_date:
                release_dates.append(release_date.text)
            else:
                release_date = 'no release date'
                release_dates.append(release_date)

            # scrape the movie name
            movie_name = items[2].find('a')
            if movie_name:
                movie_names.append(movie_name.text)
            else:
                movie_name = 'no movie name'
                movie_names.append(movie_name)

            # scrape the production budget
            production_budget = items[3]
            if production_budget:
                production_budgets.append(production_budget.text)
            else:
                production_budget = 'no budget'
                production_budgets.append(production_budget)

            # scrape the domestic gross
            domestic_gross = items[4]
            if domestic_gross:
                domestic_grosses.append(domestic_gross.text)
            else:
                domestic_gross = 'no domestic gross'
                domestic_grosses.append(domestic_gross)  

            # scrape the worldwide gross
            worldwide_gross = items[5]
            if worldwide_gross:
                worldwide_grosses.append(worldwide_gross.text)
            else:
                worldwide_gross = 'no worldwide gross'
                worldwide_grosses.append(worldwide_gross)  

    print((time.time()-start_time)/60, "minutes")

    # store lists into dataframe
    thenumbers_data = pd.DataFrame({'movie': movie_names,
    'release_date': release_dates,
    'production_budget': production_budgets,
    'domestic_gross': domestic_grosses,
    'worldwide_gross': worldwide_grosses                    
    })

    return thenumbers_data

#====================================================================
### Scraper for imdb starmeter
#====================================================================

def imdbstarmeter_scraper():
    """
    Scrapes movie data from IMDB then saves as pickled dataframe
    """
    star_names = []
    star_rankings = []
    actor_or_actresses = []

    start_time = time.time()
    requests = 0

    pages = []
    first_page = 'https://www.imdb.com/search/name/?gender=male,female&ref_=rlm'
    pages.append(first_page)
    pagerange = [str(i) for i in np.arange(51, 952, 50)] #51, 952, 50 

    for page in pagerange: 
        page = 'https://www.imdb.com/search/name/?gender=male,female&start=' + page + '&ref_=rlm'                                   
        pages.append(page)

    for page in pages:

        # make a get request
        response = get(page)
        
        # pause the loop
        time.sleep(random.randint(2,8))

        # monitor the requests
        requests += 1
        elapsed_time = time.time() - start_time
        print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        clear_output(wait = True)

        # throw a warning for non-200 status codes
        if response.status_code != 200:
            warn('Request: {}; Status code: {}'.format(requests, response.status_code))

        # break the loop if the number of requests is greater than expected
        if requests > 200:
            warn('Number of requests was greater than expected.')
            break

        # parse the content of the request with beautifulsoup
        soup = BeautifulSoup(response.text, 'lxml') 
        containers = soup.find_all('div', class_='lister-item')
        
        for container in containers:
            # scrape the star's name
            star_name = container.find('img', alt=True)['alt']
            if star_name:
                star_names.append(star_name)
            else:
                star_name = 'no name'
                star_names.append(star_name)

            # scrape the star's ranking
            star_ranking = container.find('span', class_="lister-item-index")
            if star_ranking:
                star_rankings.append(star_ranking.text)
            else:
                star_ranking = 'no ranking'
                star_rankings.append(star_ranking)

            # scrape if star is actor or actress
            actor_or_actress = container.find('p', class_='text-muted').find(text=True, recursive=False)    
            if actor_or_actress:
                actor_or_actresses.append(actor_or_actress)
            else:
                actor_or_actress = 'no type'
                actor_or_actresses.append(actor_or_actress)
    
    print((time.time()-start_time)/60, "minutes")

    # store lists into dataframe
    star_ranking_data = pd.DataFrame({'star_name': star_names,
    'star_ranking': star_rankings,
    'actor_or_actress': actor_or_actresses,
    })

    return star_ranking_data

