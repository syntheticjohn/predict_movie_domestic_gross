"""
Predicting Movie Revenue --
Functions for data preprocessing
Functions are imported and executed in the __main__.py file
"""

import pandas as pd
import pickle
from datetime import datetime

from movies_web_scraping import imdb_scraper, thenumbers_scraper, imdbstarmeter_scraper

#====================================================================
### Cleaning the scraped imdb data
#====================================================================

def clean_imdb():
    """
    Takes in scraped imdb data, returns cleaned imdb data
    """
    # read data
    imdb_data = imdb_scraper()

    # clean up the year feature
    imdb_data.loc[:, 'year'] = imdb_data['year'].str[-5:-1]

    # converted year to int
    imdb_data.year = imdb_data.year.astype(int) 

    # drop records with missing metascore
    imdb_data = imdb_data[imdb_data.metascore != 'no metascore'] 
    imdb_data.metascore = imdb_data.metascore.astype(float)

    # convert datatype of runtime feature to integer
    imdb_data.runtime = imdb_data.runtime.str.slice(0, -4) # stripped min from runtime
    imdb_data.runtime = imdb_data.runtime.astype(int) # converted runtime to int

    # filter for certain certificates
    imdb_data = imdb_data[imdb_data.certificate.isin(['G', 'PG', 'PG-13', 'R', 'NC-17', 'Not Rated', 'not rated', 'Unrated'])]                                
    #excluded ratings of ['TV-14', 'TV-MA', 'TV-PG', 'TV-G', 'TV-Y7', 'TV-Y7-FV', 'A0', 'M', 'X', 'Approved']

    # clean up format of certificate
    imdb_data['certificate'] = imdb_data['certificate'].str.replace('not rated','Not Rated')
    imdb_data['certificate'] = imdb_data['certificate'] = imdb_data['certificate'].str.replace('Unrated','Not Rated')

    # create a new feature as genre count
    imdb_data['genre_count'] = imdb_data.genre.str.len() 

    # explode the genre and stars features into rows
    imdb_data = imdb_data.explode('genre').reset_index(drop=True)
    imdb_data = imdb_data.explode('stars').reset_index(drop=True)

    # remove comma from genre
    imdb_data['genre'] = imdb_data['genre'].str.replace(',', '')

    return imdb_data

#====================================================================
### Cleaning the scraped numbers data
#====================================================================

def clean_thenumbers():
    """
    Takes in scraped the numbers data, returns cleaned the numbers data
    """
    # read data
    thenumbers_data = thenumbers_scraper()

    # remove records with unknown release dates
    thenumbers_data = thenumbers_data[thenumbers_data.release_date.str.len() >= 11] 

    # format release date
    thenumbers_data['release_date'] = pd.to_datetime(thenumbers_data['release_date'], format='%b %d, %Y')

    # convert datatype of budget and gross features to numeric type
    thenumbers_data['production_budget'] = thenumbers_data['production_budget'].str.replace(',', '').str.replace('$', '').astype(int)
    thenumbers_data['domestic_gross'] = thenumbers_data['domestic_gross'].str.replace(',', '').str.replace('$', '').astype(int)
    thenumbers_data['worldwide_gross'] = thenumbers_data['worldwide_gross'].str.replace(',', '').str.replace('$', '').astype(int)      

    # create new feature as year
    thenumbers_data['year'] = thenumbers_data['release_date'].dt.year

    return thenumbers_data

#====================================================================
### Cleaning the scraped stars data
#====================================================================

def clean_stars():
    """
    Takes in scraped stars data, returns cleaned stars data
    """
    # read data
    star_data = imdbstarmeter_scraper()

    # remove period and space char in star ranking feature
    star_data.star_ranking = star_data.star_ranking.str[:-2]

    # remove \n and space char in actor or actress feature
    star_data.actor_or_actress = star_data.actor_or_actress.str.strip()

    # add a new feature called star points (representing reverse order of star ranking number)
    star_data['star_points'] = star_data.star_ranking.values[::-1]

    # convert datatype of star ranking and star points to int
    star_data['star_ranking'] = star_data.star_ranking.str.replace(',','').astype(int)
    star_data['star_points'] = star_data.star_points.str.replace(',','').astype(int)

    return star_data

#====================================================================
### Merge imdb, the numbers and stars data
#====================================================================

def merge_data():
    """
    Takes in cleaned imdb, the numbers and stars data, returns merged data
    """
    # read in clean datasets
    imdb_data = clean_imdb()
    thenumbers_data = clean_thenumbers()
    star_data = clean_stars()

    # merge imdb and the numbers
    merged_df = pd.merge(imdb_data, thenumbers_data, how='left', left_on=['movie', 'year'], right_on=['movie', 'year'])

    # drop rows with missing values under release date
    merged_df.dropna(subset=['release_date'], inplace=True)

    # exclude films released in 2020 or yet to be released
    merged_df = merged_df[merged_df.release_date < 'Jan 1, 2020'] 

    # merge with stars data
    merged_df = pd.merge(merged_df, star_data, how='left', left_on=['stars'], right_on=['star_name'])

    # if actor or actress not in top 1000 list, then default to 0 star points
    merged_df['star_points'].fillna(0, inplace=True)

    # convert datatype of budget and gross features to integer
    merged_df.production_budget = merged_df.production_budget.astype(int)
    merged_df.domestic_gross = merged_df.domestic_gross.astype(int)
    merged_df.worldwide_gross = merged_df.worldwide_gross.astype(int)

    return merged_df

#====================================================================
### Feature engineering
#====================================================================

def engineer_features():
    """
    Takes in merged data, returns merged data with engineered features
    """
    # read in merged data
    merged_df = merge_data()

    # create new features as star power and star appearances 
    merged_df_reduced = merged_df[['movie','release_date','stars','domestic_gross']].drop_duplicates()
    merged_df_reduced['star_power'] = merged_df_reduced.apply(lambda x: merged_df_reduced[(merged_df_reduced['stars'] == x['stars'])&(merged_df_reduced['release_date'] < x['release_date'])].domestic_gross.mean(), axis=1)
    merged_df_reduced['star_appearances'] = merged_df_reduced.apply(lambda x: merged_df_reduced[(merged_df_reduced['stars'] == x['stars'])&(merged_df_reduced['release_date'] < x['release_date'])].shape[0], axis=1)
    merged_df = merged_df.merge(merged_df_reduced)

    # fill missing values in star power with zeroes
    merged_df['star_power'].fillna(0, inplace=True)

    # create a new feature as director power
    # sort values by ascending release date
    merged_df = merged_df.sort_values(by='release_date', ascending=True)
    merged_df['director_power'] = merged_df.apply(
        lambda x: merged_df[(merged_df.director == x.director) & (merged_df.release_date < x.release_date)].domestic_gross.mean(), axis=1)

    # fill in missing values with zeroes
    merged_df['director_power'].fillna(0, inplace=True)

    # create new features as title length and month
    # convert datatype of budget and gross features to integer
    merged_df.production_budget = merged_df.production_budget.astype(int)
    merged_df.domestic_gross = merged_df.domestic_gross.astype(int)
    merged_df.worldwide_gross = merged_df.worldwide_gross.astype(int)

    # create a new feature as number of characters in movie title
    merged_df['title_length'] = merged_df.movie.str.len() 

    # create a new feature as month of movie release
    merged_df['month'] = merged_df['release_date'].dt.strftime('%b') 

    return merged_df

#====================================================================
### Aggregate the stars and genre data
#====================================================================

def agg_stars_genre():
    """
    Takes in merged data with engineered features, returns aggregated data on stars and genre
    """
    # read in merged data with engineered features
    merged_df = engineer_features()
    
    # aggregate the stars data, by averaging the "star power" and "star points", and summing the "star appearances" for each movie
    groupby_cols = ['movie', 'year', 'imdb', 'metascore', 'votes', 'runtime', 'title_length',
                    'certificate', 'genre', 'genre_count', 'director', 'release_date', 'month',
                    'production_budget', 'domestic_gross', 'worldwide_gross',
                    'director_power']
    movies_genre_df = merged_df.groupby(groupby_cols).agg({'star_power':'mean', 'star_points':'mean', 'star_appearances':'sum'}).reset_index()

    # collapse genres of movies into genre count (to get 1 row per movie)
    groupby_cols = ['movie', 'year', 'imdb', 'metascore', 'votes', 'runtime', 'title_length',
                    'certificate', 'genre_count', 'director', 'release_date', 'month',
                    'production_budget', 'domestic_gross', 'worldwide_gross',
                    'director_power', 'star_power', 'star_appearances', 'star_points']
    movies_df = movies_genre_df[groupby_cols].drop_duplicates(subset=['movie', 'release_date'])
    movies_df.reset_index(drop=True, inplace=True)                       

    # rearrange columns
    movies_df = movies_df[['movie', 'imdb', 'metascore', 'votes', 'runtime', 'certificate',
                        'year', 'month', 'release_date', 'genre_count',
                        'director', 'title_length', 'production_budget',   
                        'director_power', 'star_power', 'star_appearances', 'star_points',
                        'worldwide_gross', 'domestic_gross']]  

    # pickle dataframes for eda and modeling               
    movies_df.to_pickle('data/movies_df.pkl')
    movies_genre_df.to_pickle('data/movies_genre_df.pkl')