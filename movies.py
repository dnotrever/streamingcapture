import time
import re
import os
import traceback
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from custom_traceback import traceback_formatted

from selenium_core import sc

class Movies:

    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv('BASE_URL')
        self.movies_url = os.getenv('MOVIES_URL')
        self.source_1_movies = os.getenv('SOURCE_1_MOVIES')
        self.source_2_movies = os.getenv('SOURCE_2_MOVIES')

    def close_spam_tabs(self, actived_tabs):

        if sc.tab('count') > actived_tabs:
            for _ in range(sc.tab('count') - actived_tabs):
                sc.tab(actived_tabs, 'select')
                sc.close()
    
    def roman_to_integer(self, movie):
        pattern = r'\b(I{1,3}|IV|V|IX|X{1,3})\b'
        def replace(match):
            roman_numeral = match.group(0)
            roman_to_number = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'IX': 9, 'X': 10}
            return str(roman_to_number.get(roman_numeral, roman_numeral))
        result = re.sub(pattern, replace, movie)
        return result

    def platform_login(self):

        sc.tab(1)
        
        sc.get(self.base_url + '/login')
    
        user_email = os.getenv('EMAIL')
        user_password = os.getenv('PASSWORD')
        
        sc.element('id', 'email').send_keys(user_email)
        sc.element('id', 'password').send_keys(user_password)
        sc.click('class', 'btn')

    def get_movie_video(self, movie, movie_code):

        sc.tab(2)

        video = self.source_1_movies + movie_code

        movie = self.roman_to_integer(movie)

        movie_query = re.sub(r'[^\w]+', '+', movie.lower())

        try:
            
            ## Alternative 1
            
            sc.get(self.source_2_movies + '?s=' + movie_query)

            movies_list = sc.element('class', 'items')
            
            movies_items = sc.element('tag', 'a', 'all', movies_list)

            for item in movies_items:
                title = item.get_attribute('title').split(' (')[0]
                if title.lower() == movie.lower():
                    item.click()
                    break

            sc.click('selector', 'button[name="play"]')

            divPlay = sc.element('class', 'play')
            linksPlay = sc.element('class', 'btn', 'all', divPlay)

            for link in linksPlay:
                try:
                    alternative = link.get_attribute('href')
                    break
                except:
                    continue
        
        except:

            pass

        self.close_spam_tabs(3)

        return video, alternative

    def get_movie_cover(self, movie_title):

        movie_query = re.sub(r'[^\w]+', '-', movie_title.lower())

        sc.get('https://www.themoviedb.org/search/movie?query=' + movie_query)
        
        movie_list = sc.element('class', 'card', 'all')
        
        for movie in movie_list:
            
            title = movie.text.split('\n')[0]
            
            if title == movie_title:
                
                cover_url = sc.element('tag', 'img', 'one', movie).get_attribute('src')
                movie_cover = cover_url.split('/')[6]
                
                break

        sc.close()

        return movie_cover

    def dataframe_create(self, movies):
        
        movie_data = []

        for movie in movies:
            movie_data.append([
                movie['title'],
                '; '.join(movie['categories']),
                movie['release'],
                '; '.join(movie['directors']),
                '; '.join(movie['writers']),
                '; '.join(movie['production']),
                movie['country'],
                movie['video'],
                movie['alternative'],
                movie['cover'],
                movie['synopsis'],
            ])

        movie_infos = pd.DataFrame(movie_data, columns=['Title', 'Categories', 'Release', 'Directors', 'Writers', 'Production', 'Country', 'Video', 'Alternative', 'Cover', 'Synopsis'])

        return movie_infos

    def movie_insert(self, movies):
        
        sc.tab(1, 'select')

        sc.get(self.movies_url + 'insert')

        for index, row in movies.iterrows():
        
            mapping = {
                'Title': 'title',
                'Categories': 'categories',
                'Release': 'released',
                'Directors': 'director',
                'Writers': 'writer',
                'Production': 'production',
                'Country': 'country',
                'Video': 'video',
                'Alternative': 'alternative',
                'Cover': 'cover',
                'Synopsis': 'synopsis',
            }

            for key, value in mapping.items():
                field_id = value
                field_value = row[key]
                if pd.isna(field_value): field_value = ''
                sc.element('id', field_id).send_keys(field_value)

        sc.click('selector', 'button[type="submit"]')

    def movie_infos(self, movies):
        
        try:

            if sc.tab('count') == 1:
                self.platform_login()
            
            for movie in movies:

                sc.tab(0, 'select')
                
                ## Get Movie Search
                movie_query = re.sub(r'[^a-z0-9 ]', '', movie.lower()).replace(' ', '%20')
                sc.get('https://www.imdb.com/find/?q=' + movie_query + '&ref_=nv_sr_sm')

                ## Select Movie Title
                search_serie_title = sc.element('selector', 'section[data-testid="find-results-section-title"]')
                sc.element('class', 'find-title-result', 'one', search_serie_title).click()

                movie_code = sc.current_url().split('/')[4]

                movies_list = []
                movie_infos = {'title': '', 'categories': [], 'directors': [], 'writers': [], 'release': '', 'production': [], 'country': '', 'synopsis': '', 'cover': '', 'video': '', 'alternative': '' }

                sc.action('end')
                time.sleep(1.5)
            
                ## Title
                movie_title = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span').text
                movie_infos['title'] = movie_title

                ## Categories
                movie_categories = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]')
                categories_names = sc.element('class', 'ipc-chip__text', 'all', movie_categories)
                for category in categories_names:
                    movie_infos['categories'].append(category.text)
                
                ## Synopsis
                movie_synopsis = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]').text
                movie_infos['synopsis'] = movie_synopsis
                
                ## Directors
                movie_directors = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]')
                directors_names = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'all', movie_directors)
                for director in directors_names:
                    movie_infos['directors'].append(director.text)

                ## Writers
                movie_writers = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]')
                writers_names = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'all', movie_writers)
                for writer in writers_names:
                    movie_infos['writers'].append(writer.text)

                ## Release
                movie_release = sc.element('selector', 'li[data-testid="title-details-releasedate"]')

                ## Date
                release_date = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'one', movie_release).text.split(' (')[0]
                movie_infos['release'] = datetime.strptime(release_date, "%B %d, %Y").strftime("%d/%m/%Y")
                
                ## Country
                movie_country = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'one', movie_release).text.split(' (')[1]
                movie_infos['country'] = movie_country.replace(')', '')

                ## Productions
                movie_productions = sc.element('selector', 'li[data-testid="title-details-companies"]')
                productions_names = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'all', movie_productions)
                for production in productions_names:
                    movie_infos['production'].append(production.text)
                    
                    movie_video = alternative_video = ''
                
                if datetime.strptime(release_date, "%B %d, %Y") < datetime.today():

                    sc.tab(1, 'select')

                    movie_video, alternative_video = self.get_movie_video(movie_title, movie_code)

                    sc.tab(2, 'select')
                    
                else:
                    
                    sc.tab(2)

                movie_cover = self.get_movie_cover(movie_title)

                movie_infos['video'] = movie_video
                movie_infos['alternative'] = alternative_video
                movie_infos['cover'] = movie_cover

                movies_list.append(movie_infos)
                
                df_movie = self.dataframe_create(movies_list)
                
                self.movie_insert(df_movie)
            
            return ['success', 'Successfully movies add!']

        except:
            
            return ['error', traceback_formatted(traceback.format_exc())]


# sc.set_driver()
# test = Movies()
# test.get_movie_cover('The Marvels')