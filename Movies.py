import pandas as pd
import time, re, os
from datetime import datetime
from dotenv import load_dotenv

from Selenium import By, Keys
from Selenium import get_wait, get_actions, clickable, located, all_located

class Movies:

    def __init__(self, driver):
        
        self.driver = driver
        
        self.wait = get_wait(self.driver)
        self.actions = get_actions(self.driver)
        
        load_dotenv()
        self.base_url = os.getenv('BASE_URL')
        self.movies_url = os.getenv('MOVIES_URL')
        self.source_1_movies = os.getenv('SOURCE_1_MOVIES')
        self.source_2_movies = os.getenv('SOURCE_2_MOVIES')

    def close_spam_tabs(self, actived_tabs):

        if len(self.driver.window_handles) > actived_tabs:
            for _ in range(len(self.driver.window_handles) - actived_tabs):
                self.driver.switch_to.window(self.driver.window_handles[actived_tabs])
                self.driver.close()
    
    def roman_to_integer(self, movie):

        pattern = r'\b(I{1,3}|IV|V|IX|X{1,3})\b'
        
        def replace(match):
            roman_numeral = match.group(0)
            roman_to_number = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'IX': 9, 'X': 10}
            return str(roman_to_number.get(roman_numeral, roman_numeral))
        
        result = re.sub(pattern, replace, movie)
        return result

    def platform_login(self):

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(self.base_url + '/login')
    
        user_email = os.getenv('EMAIL')
        user_password = os.getenv('PASSWORD')
        
        self.wait.until(clickable((By.ID, 'email'))).send_keys(user_email)
        self.wait.until(clickable((By.ID, 'password'))).send_keys(user_password)
        self.wait.until(clickable((By.CLASS_NAME, 'btn'))).click()

    def get_movie_video(self, movie, movie_code):

        self.driver.switch_to.window(self.driver.window_handles[2])

        video = self.source_2_movies + movie_code

        movie = self.roman_to_integer(movie)

        movie_query = re.sub(r'[^\w]+', '+', movie.lower())

        self.driver.get(self.source_1_movies + '?s=' + movie_query)

        try:

            self.wait.until(clickable((By.XPATH, '/html/body/div[1]/form/div[6]/div'))).click()

            self.wait.until(clickable((By.CSS_SELECTOR, 'button[name="play"]'))).click()

            divPlay = self.wait.until(located((By.CLASS_NAME, 'play')))

            linksPlay = get_wait(divPlay).until(all_located((By.CLASS_NAME, 'btn')))

            for link in linksPlay:
                try:
                    video = link.get_attribute('href')
                    break
                except:
                    continue
        
        except:

            pass

        self.close_spam_tabs(3)

        return video

    def get_movie_cover(self, movie):
        
        # self.driver.switch_to.window(self.driver.window_handles[2])

        serie_query = re.sub(r'[^\w]+', '-', movie.lower())

        self.driver.get('https://www.themoviedb.org/search/movie?query=' + serie_query)

        ## Getting Cover
        cover_url = self.wait.until(clickable((By.XPATH, '/html/body/div[1]/main/section/div/div/div[2]/section/div[1]/div/div[1]/div/div[1]/div/a/img'))).get_attribute('src')
        serie_cover = cover_url.split('/')[6]

        self.driver.close()

        return serie_cover

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
                movie['cover'],
                movie['synopsis'],
            ])

        movie_infos = pd.DataFrame(movie_data, columns=['Title', 'Categories', 'Release', 'Directors', 'Writers', 'Production', 'Country', 'Video', 'Cover', 'Synopsis'])

        return movie_infos

    def movie_insert(self, movies):

        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get(self.movies_url + 'insert')

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
                'Cover': 'cover',
                'Synopsis': 'synopsis',
            }

            for key, value in mapping.items():
                field_id = value
                field_value = row[key]
                if pd.isna(field_value): field_value = ''
                self.wait.until(clickable((By.ID, field_id))).send_keys(field_value)

        insert_btn = self.wait.until(located((By.CSS_SELECTOR, 'button[type="submit"]')))
        self.driver.execute_script('arguments[0].click();', insert_btn)

    def movie_infos(self, movies):

        if len(self.driver.window_handles) == 1:
            self.platform_login()
        
        for movie in movies:

            self.driver.switch_to.window(self.driver.window_handles[0])
            
            ## Get Movie Search
            movie_query = re.sub(r'[^a-z0-9 ]', '', movie.lower()).replace(' ', '%20')
            self.driver.get('https://www.imdb.com/find/?q=' + movie_query + '&ref_=nv_sr_sm')

            ## Select Movie Title
            search_serie_title = self.wait.until(located((By.CSS_SELECTOR, 'section[data-testid="find-results-section-title"]')))
            result_serie_title = get_wait(search_serie_title).until(clickable((By.CLASS_NAME, 'find-title-result')))
            self.driver.execute_script('arguments[0].click();', result_serie_title)

            movie_code = self.driver.current_url.split('/')[4]

            movies_list = []
            movie_infos = {'title': '', 'categories': [], 'directors': [], 'writers': [], 'release': '', 'production': [], 'country': '', 'synopsis': '', 'cover': '', 'video': '' }

            self.actions.send_keys(Keys.END).perform()
            time.sleep(1.5)
        
            ## Title
            movie_title = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span'))).text
            movie_infos['title'] = movie_title

            ## Categories
            movie_categories = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]')))
            categories_names = get_wait(movie_categories).until(all_located((By.CLASS_NAME, 'ipc-chip__text')))
            for category in categories_names:
                movie_infos['categories'].append(category.text)
            
            ## Synopsis
            movie_synopsis = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]'))).text
            movie_infos['synopsis'] = movie_synopsis
            
            ## Directors
            movie_directors = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]')))
            directors_names = get_wait(movie_directors).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
            for director in directors_names:
                movie_infos['directors'].append(director.text)

            ## Writers
            movie_writers = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]')))
            writers_names = get_wait(movie_writers).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
            for writer in writers_names:
                movie_infos['writers'].append(writer.text)

            ## Release
            movie_release = self.wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-releasedate"]')))

            ## Date
            release_date = get_wait(movie_release).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[0]
            movie_infos['release'] = datetime.strptime(release_date, "%B %d, %Y").strftime("%d/%m/%Y")
            
            ## Country
            movie_country = get_wait(movie_release).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[1]
            movie_infos['country'] = movie_country.replace(')', '')

            ## Productions
            movie_productions = self.wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-companies"]')))
            productions_names = get_wait(movie_productions).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
            for production in productions_names:
                movie_infos['production'].append(production.text)

            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.execute_script("window.open('');")

            movie_video = self.get_movie_video(movie_title, movie_code)

            self.driver.switch_to.window(self.driver.window_handles[2])

            movie_cover = self.get_movie_cover(movie_title)

            movie_infos['video'] = movie_video
            movie_infos['cover'] = movie_cover

            movies_list.append(movie_infos)
            
            df_movie = self.dataframe_create(movies_list)
            
            self.movie_insert(df_movie)
        
        return ['success', 'Successfully movies add!']


