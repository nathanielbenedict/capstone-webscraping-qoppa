from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import numpy as np
import seaborn as sns

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url = 'https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31'
response = requests.get(url)
soup = BeautifulSoup(response.content,'html.parser')

#make empty list
movie_name = [] 
#year = [] -> not included
time = [] 
rating = []
metascore = []
votes = []

#find your right key here
movie_data = soup.find_all('div', attrs = {'class':'lister-item mode-advanced'})

for store in movie_data:
    #get movie name
    name = store.h3.a.text
    movie_name.append(name)
    
    #get year of release
    #year_of_release = store.h3.find('span', class_= 'lister-item-year text-muted unbold').text.replace('(','').replace(')','')
    #year.append(year_of_release)
    
    #get movie duration
    runtime = store.p.find('span', class_= 'runtime').text.replace(' min', '') if store.p.find('span', class_= 'runtime') else '0'
    time.append(runtime)
    
    #get movie rating
    rate = store.find('div', class_= 'inline-block ratings-imdb-rating').text.replace('\n', '')
    rating.append(rate)
    
    #get metascore
    meta = store.find('span', class_= 'metascore').text if store.find('span', class_= 'metascore') else '0'
    metascore.append(meta)
    
    #get total votes
    total_votes = store.find('span', attrs = {'name': 'nv'}).text
    votes.append(total_votes)

#change into dataframe
imdb = pd.DataFrame({'Movie Title' : movie_name, 'Duration': time, 'Movie Rating': rating, 'Metascore': metascore, 'Total Votes': votes})

#insert data wrangling here
imdb['Total Votes'] = imdb['Total Votes'].str.replace(',','')
imdb['Duration'] = imdb['Duration'].astype('int64')
imdb['Movie Rating'] = imdb['Movie Rating'].astype('float64')
imdb['Metascore'] = imdb['Metascore'].astype('int64')
imdb['Total Votes'] = imdb['Total Votes'].astype('int64')
top7_popularity = imdb.head(7).set_index('Movie Title')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{top7_popularity["Movie Rating"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = top7_popularity.plot(figsize = (20,5)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
