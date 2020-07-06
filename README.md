# Predicting Movie Revenue Before Release

**Project overview:**
- Predicted the domestic gross revenue of movies before release 
- Web-scraped ~3K movies from IMDB and The Numbers using BeautifulSoup
- Engineered "director power" and "star power" features, based on previous film revenue 
- Trained LASSO and Ridge polynomial regression models with 5-fold cross validation and a random forest model
- Random forest was selected as the final model which performed an R^2 of 0.458 on the test set

**This repo includes:**

- **movies_web_scraping.ipynb**: web scraping
- **movies_preprocessing.ipynb**: data preprocessing
- **movies_eda.ipynb**: 
- **movies_modeling.ipynb**: 
- **helper_functions.py**: 
- **data**: pickled files
- **movies_revenue_predictions_slides.pdf**: pdf of project presentation slides
