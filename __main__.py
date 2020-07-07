"""
Predicting Movie Revenue --
Script to kick off web scraping and movie preprocessing tasks
Used to create pickled dataframes for exploratory analysis and modeling
This script is designed to be run through a jupyter notebook or the command line
"""

from movies_web_scraping import imdb_scraper, thenumbers_scraper, imdbstarmeter_scraper
from movies_preprocessing import clean_imdb, clean_thenumbers, clean_stars, merge_data, engineer_features, agg_stars_genre  

#====================================================================
### Execute web scraping and preprocessing
#====================================================================

def main():
    """
    Kick off web scraping and preprocessing tasks, returns pickled dataframes for eda and modeling 
    """
    # web scrape data
    imdb_scraper()
    thenumbers_scraper()
    imdbstarmeter_scraper()

    # set recursion limit
    # sys.setrecursionlimit(10000)

    # preprocess the web scraped data
    agg_stars_genre()
 
if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main() 