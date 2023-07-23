import pandas as pd
import time, re, os
from datetime import datetime
from dotenv import load_dotenv

from Selenium import By, Keys
from Selenium import get_wait, get_actions, clickable, located, all_located

from Episodes import Episodes

class Series:
    
    def __init__(self, driver):
        
        self.driver = driver
        
        self.wait = get_wait(self.driver)
        self.actions = get_actions(self.driver)
        
        load_dotenv()
        self.base_url = os.getenv('BASE_URL')
        self.series_url = os.getenv('SERIES_URL')
        
    def platform_login(self):

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(self.base_url + '/login')
    
        user_email = os.getenv('EMAIL')
        user_password = os.getenv('PASSWORD')

        self.wait.until(clickable((By.ID, 'email'))).send_keys(user_email)
        self.wait.until(clickable((By.ID, 'password'))).send_keys(user_password)
        self.wait.until(clickable((By.CLASS_NAME, 'btn'))).click()

    def get_seasons(self, serie_code):
        
        self.driver.get(f'https://www.imdb.com/title/' + serie_code + '/episodes')
        
        serie_title = self.wait.until(located((By.CSS_SELECTOR, 'h3[itemprop="name"]')))
        serie_dates = get_wait(serie_title).until(located((By.CLASS_NAME, 'nobr')))
        
        try: conclusion_year = re.sub(r'^\s*\(|\)\s*$', '', serie_dates.text).split('–')[1]
        except: conclusion_year = serie_dates.text
        
        season_list  = self.wait.until(located((By.ID, 'bySeason')))
        season_count = get_wait(season_list ).until(all_located((By.TAG_NAME, 'option')))

        if conclusion_year == ' ':
            return len(season_count ) - 1
        else:
            return len(season_count )

    def get_serie_cover(self, serie):

        self.driver.switch_to.window(self.driver.window_handles[2])

        serie_query = re.sub(r'[^\w]+', '-', serie.lower())

        self.driver.get('https://www.themoviedb.org/search/tv?query=' + serie_query)
        
        serie_cover = ''
        
        ## Getting Cover
        cover_url = self.wait.until(clickable((By.XPATH, '/html/body/div[1]/main/section/div/div/div[2]/section/div[1]/div/div[1]/div/div[1]/div/a/img'))).get_attribute('src')
        serie_cover = cover_url.split('/')[6]

        self.driver.close()

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
        
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get(self.series_url + 'insert')
            
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
                self.wait.until(clickable((By.ID, field_id))).send_keys(field_value)

        insert_btn = self.wait.until(located((By.CSS_SELECTOR, 'button[type="submit"]')))
        self.driver.execute_script('arguments[0].click();', insert_btn)

    def serie_infos(self, series):

        if len(self.driver.window_handles) == 1:
            self.platform_login()
        
        for serie in series:
            
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            ## Get Serie Search
            serie_query = re.sub(r'[^a-z0-9 ]', '', serie.lower()).replace(' ', '%20')
            self.driver.get('https://www.imdb.com/find/?q=' + serie_query + '&ref_=nv_sr_sm')
        
            ## Select Serie Title
            search_serie_title = self.wait.until(located((By.CSS_SELECTOR, 'section[data-testid="find-results-section-title"]')))
            result_serie_title = get_wait(search_serie_title).until(clickable((By.CLASS_NAME, 'find-title-result')))
            self.driver.execute_script('arguments[0].click();', result_serie_title)
            
            serie_code = self.driver.current_url.split('/')[4]
            
            series_list = []
            serie_infos = {'title': '', 'categories': [], 'creators': [], 'seasons': '', 'release': '', 'production': [], 'country': '', 'conclusion': '', 'synopsis': '', 'cover': ''}
            
            self.actions.send_keys(Keys.END).perform()
            time.sleep(1.5)

            ## Title
            serie_title = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span'))).text
            serie_infos['title'] = serie_title

            ## Categories
            serie_categories = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]')))
            categories_names = get_wait(serie_categories).until(all_located((By.CLASS_NAME, 'ipc-chip__text')))
            for category in categories_names:
                serie_infos['categories'].append(category.text)
            
            ## Synopsis
            serie_synopsis = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]'))).text
            serie_infos['synopsis'] = serie_synopsis
            
            ## Creators
            serie_creators = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]')))
            creators_names = get_wait(serie_creators).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
            for creator in creators_names:
                serie_infos['creators'].append(creator.text)
            
            ## Release
            serie_release = self.wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-releasedate"]')))

            ## Date
            release_date = get_wait(serie_release).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[0]
            serie_infos['release'] = datetime.strptime(release_date, "%B %d, %Y").strftime("%d/%m/%Y")
            
            ## Country
            serie_country = get_wait(serie_release).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[1]
            serie_infos['country'] = serie_country.replace(')', '')

            ## Productions
            serie_productions = self.wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-companies"]')))
            productions_names = get_wait(serie_productions).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
            for production in productions_names:
                serie_infos['production'].append(production.text)

            serie_seasons_count = self.get_seasons(serie_code)
            
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.execute_script("window.open('');")
            
            serie_cover = self.get_serie_cover(serie_title)
            
            serie_infos['seasons'] = serie_seasons_count
            serie_infos['cover'] = serie_cover

            series_list.append(serie_infos)
            
            df_series = self.dataframe_create(series_list)
            
            self.serie_insert(df_series)

            insert_episodes = Episodes(self.driver)
            insert_episodes.episodes_infos(serie_title, 'all', False)
            
        return ['success', 'Successfully series add!']


