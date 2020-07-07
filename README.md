# Predicting Movie Revenue Before Release

**Project overview:**
- Predicted the domestic gross revenue of movies before release 
- Web-scraped and preprocessed ~3K movies from IMDB and The Numbers using Requests and BeautifulSoup
- Engineered "director power" and "star power" features, based on previous film revenue 
- Trained LASSO and Ridge polynomial regression models with 5-fold cross validation and a random forest model
- Random forest was selected as the final model which performed an R^2 of 0.498 on the test set

**This repo includes:**

- **__main__.py**: main py file to execute web scraping and data preprocessing tasks
- **movies_web_scraping.py**: web scraping functions 
- **movies_preprocessing.py**: data preprocessing and feature engineering functions
- **movies_eda.ipynb**: exploratory analysis 
- **movies_modeling.ipynb**: modeling
- **helper_functions.py**: 
- **data**: pickled files
- **movies_revenue_predictions_slides.pdf**: pdf of project presentation slides
