import time
import re
import os
import traceback
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from custom_traceback import traceback_formatted
from episodes import Episodes

from selenium_core import sc

class Series:
    
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv('BASE_URL')
        self.series_url = os.getenv('SERIES_URL')
        
    def platform_login(self):

        sc.tab(1)
        
        sc.get(self.base_url + '/login')
    
        user_email = os.getenv('EMAIL')
        user_password = os.getenv('PASSWORD')
        
        sc.element('id', 'email').send_keys(user_email)
        sc.element('id', 'password').send_keys(user_password)
        sc.click('class', 'btn')

    def get_seasons(self, serie_code):
        
        serie_infos = sc.element('class', 'kdXikI')
        serie_dates = sc.element('class', 'ipc-inline-list__item', 'all', serie_infos)[1]
        
        conclusion_year = (serie_dates.text).split('–')[1]

        sc.get(f'https://www.imdb.com/title/' + serie_code + '/episodes')
        
        season_list  = sc.element('xpath', '/html/body/div[2]/main/div/section/div/section/div/div[1]/section[2]/section[1]/div[2]/ul')
        season_count = sc.element('class', 'ipc-tab--on-base', 'all', season_list)

        if not conclusion_year:
            return len(season_count) - 1
        else:
            return len(season_count)

    def get_serie_cover(self, serie):

        sc.tab(2, 'select')

        serie_query = re.sub(r'[^\w]+', '-', serie.lower())

        sc.get('https://www.themoviedb.org/search/tv?query=' + serie_query)
        
        serie_cover = ''
        
        ## Getting Cover
        cover_url = sc.element('xpath', '/html/body/div[1]/main/section/div/div/div[2]/section/div[1]/div/div[1]/div/div[1]/div/a/img').get_attribute('src')
        serie_cover = cover_url.split('/')[6]

        sc.close()

        return serie_cover

    def dataframe_create(self, series):
        
        serie_data = []

        for serie in series:
            serie_data.append([
                serie['title'],
                '; '.join(serie['categories']),
                '; '.join(serie['creators']),
                serie['seasons'],
                serie['release'],
                '; '.join(serie['production']),
                serie['country'],
                serie['conclusion'],
                serie['synopsis'],
                serie['cover']
            ])

        serie_infos = pd.DataFrame(serie_data, columns=['Title', 'Categories', 'Creators', 'Seasons', 'Release', 'Production', 'Country', 'Conclusion', 'Synopsis', 'Cover'])

        return serie_infos

    def serie_insert(self, series):
        
        sc.tab(1, 'select')

        sc.get(self.series_url + 'insert')
            
        for index, row in series.iterrows():

            mapping = {
                'Title': 'title',
                'Categories': 'categories',
                'Creators': 'creator',
                'Seasons': 'seasons',
                'Release': 'released',
                'Production': 'production',
                'Conclusion': 'ended',
                'Country': 'country',
                'Synopsis': 'synopsis',
                'Cover': 'cover',
            }

            for key, value in mapping.items():
                field_id = value
                field_value = row[key]
                if pd.isna(field_value): field_value = ''
                sc.element('id', field_id).send_keys(field_value)

        sc.click('selector', 'button[type="submit"]')

    def serie_infos(self, series):
        
        try:
            
            if sc.tab('count') == 1:
                self.platform_login()
            
            for serie in series:
                
                sc.tab(0, 'select')
                
                ## Get Serie Search
                serie_query = re.sub(r'[^a-z0-9 ]', '', serie.lower()).replace(' ', '%20')
                sc.get('https://www.imdb.com/find/?q=' + serie_query + '&ref_=nv_sr_sm')
            
                ## Select Serie Title
                search_serie_title = sc.element('selector', 'section[data-testid="find-results-section-title"]')
                sc.element('class', 'find-title-result', 'one', search_serie_title).click()
                
                serie_code = sc.current_url().split('/')[4]
                
                series_list = []
                serie_infos = {'title': '', 'categories': [], 'creators': [], 'seasons': '', 'release': '', 'production': [], 'country': '', 'conclusion': '', 'synopsis': '', 'cover': ''}
                
                sc.action('end')
                time.sleep(1.5)

                ## Title
                serie_title = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span').text
                serie_infos['title'] = serie_title

                ## Categories
                serie_categories = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]')
                categories_names = sc.element('class', 'ipc-chip__text', 'all', serie_categories)
                for category in categories_names:
                    serie_infos['categories'].append(category.text)
                
                ## Synopsis
                serie_synopsis = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]').text
                serie_infos['synopsis'] = serie_synopsis
                
                ## Creators
                serie_creators = sc.element('xpath', '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]')
                creators_names = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'all', serie_creators)
                for creator in creators_names:
                    serie_infos['creators'].append(creator.text)
                
                ## Release
                serie_release = sc.element('selector', 'li[data-testid="title-details-releasedate"]')

                ## Date
                release_date = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'one', serie_release).text.split(' (')[0]
                serie_infos['release'] = datetime.strptime(release_date, "%B %d, %Y").strftime("%d/%m/%Y")
                
                ## Country
                serie_country = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'one', serie_release).text.split(' (')[1]
                serie_infos['country'] = serie_country.replace(')', '')

                ## Productions
                serie_productions = sc.element('selector', 'li[data-testid="title-details-companies"]')
                productions_names = sc.element('class', 'ipc-metadata-list-item__list-content-item', 'all', serie_productions)
                for production in productions_names:
                    serie_infos['production'].append(production.text)

                serie_seasons_count = self.get_seasons(serie_code)
                
                sc.tab(2)
                
                serie_cover = self.get_serie_cover(serie_title)
                
                serie_infos['seasons'] = serie_seasons_count
                serie_infos['cover'] = serie_cover

                series_list.append(serie_infos)
                
                df_series = self.dataframe_create(series_list)
                
                self.serie_insert(df_series)
                
                # time.sleep(3600)
                
                insert_episodes = Episodes()
                insert_episodes.episodes_infos(serie_title, 'all', serie_seasons_count)
                
            return ['success', 'Successfully series add!']

        except:
            
            return ['error', traceback_formatted(traceback.format_exc())]

