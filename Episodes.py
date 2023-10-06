import pandas as pd
import time, re, os
from datetime import datetime
from dotenv import load_dotenv

from streamingcapture.selenium_core import By, Keys
from streamingcapture.selenium_core import get_wait, get_actions, clickable, located, all_located

class Episodes:
    
    def __init__(self, driver):
        
        self.driver = driver
        
        self.wait = get_wait(self.driver)
        self.actions = get_actions(self.driver)
        
        load_dotenv()
        self.base_url = os.getenv('BASE_URL')
        self.series_url = os.getenv('SERIES_URL')
        self.source_1_series = os.getenv('SOURCE_1_SERIES')
        self.source_2_series = os.getenv('SOURCE_2_SERIES')
    
    def close_spam_tabs(self, actived_tabs):

        if len(self.driver.window_handles) > actived_tabs:
            for _ in range(len(self.driver.window_handles) - actived_tabs):
                self.driver.switch_to.window(self.driver.window_handles[actived_tabs])
                self.driver.close()

    def platform_login(self):

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(self.base_url + '/login')
    
        user_email = os.getenv('EMAIL')
        user_password = os.getenv('PASSWORD')
        
        self.wait.until(clickable((By.ID, 'email'))).send_keys(user_email)
        self.wait.until(clickable((By.ID, 'password'))).send_keys(user_password)
        self.wait.until(clickable((By.CLASS_NAME, 'btn'))).click()

    def get_episode_video(self, serie_code, season_value, episode_number):

        self.driver.switch_to.window(self.driver.window_handles[2])
        
        video = self.source_2_series + serie_code + '-' + str(season_value) + '-' + str(episode_number)

        try:

            seasons_container = self.wait.until(all_located((By.CSS_SELECTOR, 'form[method="post"]')))
        
            number_pad = str(episode_number).zfill(2)
            
            episodes_button = get_wait(seasons_container[int(season_value)-1]).until(all_located((By.TAG_NAME, 'button')))
            
            for episode in episodes_button:
                if number_pad in re.findall(r'\d{2}', episode.text):
                    self.driver.execute_script('arguments[0].click();', episode)
                    video = self.wait.until(located((By.XPATH, '/html/body/div[1]/iframe'))).get_attribute('src')
                    break
                    
        except: 
            
            pass
            
        self.close_spam_tabs(3)
        
        return video

    def dataframe_create(self, episodes):
        
        data = []

        for episode in episodes:
            data.append([
                episode['number'],
                episode['title'],
                episode['video'],
                episode['release'],
            ])

        main_infos = pd.DataFrame(data, columns=['Number', 'Title', 'Video', 'Release'])

        return main_infos

    def episodes_insert(self, serie_url, season, episodes):

        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get(self.series_url + serie_url + '/' + season + '/episodes-control')
            
        for index, row in episodes.iterrows():

            if index < len(episodes):
                    
                mapping = {
                    'Title': f'title_{index}',
                    'Video': f'video_{index}',
                    'Release': f'released_{index}',
                }

                for key, value in mapping.items():

                    field_id = value
                    field_value = row[key]

                    if pd.isna(field_value): field_value = ''

                    input_field = self.wait.until(clickable((By.ID, field_id)))
                    
                    input_field.clear()
                    input_field.send_keys(field_value)

                if index < len(episodes) - 1:
                    add_episode = self.wait.until(located((By.ID, 'add-episode')))
                    self.driver.execute_script('arguments[0].click();', add_episode)
                
        episode_form = self.wait.until(located((By.CLASS_NAME, 'App_episodesControlForm')))
        insert_btn = get_wait(episode_form).until(located((By.CSS_SELECTOR, 'button[type="submit"]')))
        self.driver.execute_script('arguments[0].click();', insert_btn)

    def episodes_infos(self, serie_title, season_value, default_source):

        if len(self.driver.window_handles) == 1:
            self.platform_login()
        
        default_source_url = lambda season_value, number: self.source_2_series + serie_code + '-' + season_value + '-' + str(number)

        self.driver.switch_to.window(self.driver.window_handles[0])

        ## Get Serie Search
        serie_query = re.sub(r'[^a-z0-9 ]', '', serie_title.lower()).replace(' ', '%20')
        self.driver.get('https://www.imdb.com/find/?q=' + serie_query + '&ref_=nv_sr_sm')

        ## Select Serie Title
        search_serie_title = self.wait.until(located((By.CSS_SELECTOR, 'section[data-testid="find-results-section-title"]')))
        result_serie_title = get_wait(search_serie_title).until(clickable((By.CLASS_NAME, 'find-title-result')))
        self.driver.execute_script('arguments[0].click();', result_serie_title)
        
        serie_code = self.driver.current_url.split('/')[4]

        serie_title = self.wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span'))).text
        serie_url = re.sub(r'[^\w]+', '-', serie_title.lower())

        if not default_source:

            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.execute_script("window.open('');")

            self.driver.switch_to.window(self.driver.window_handles[2])

            try:
                self.driver.get(self.source_1_series + serie_url)
            except:
                self.driver.close()
                default_source = True

            self.driver.switch_to.window(self.driver.window_handles[0])

        if season_value != 'all':
            
            episodes_list = []
            
            episode_number = 0
            
            self.driver.get(f'https://www.imdb.com/title/' + serie_code + '/episodes?season=' + season_value)
            
            episodes = self.wait.until(all_located((By.CSS_SELECTOR, 'div[itemprop="episodes"]')))
            
            for episode in episodes:
                
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                episodes_infos = {'number': '', 'title': '', 'video': '', 'release': ''}
                
                episode_number += 1

                ## Title
                episode_title = get_wait(episode).until(located((By.CSS_SELECTOR, 'a[itemprop="name"]'))).text
                
                ## Release
                episode_release = get_wait(episode).until(located((By.CLASS_NAME, 'airdate'))).text
                release_format = datetime.strptime(episode_release.replace('.', ''), "%d %b %Y").strftime("%d/%m/%Y")

                ## Video
                episode_video = default_source_url(season_value, episode_number) if default_source else self.get_episode_video(serie_code, season_value, episode_number)

                episodes_infos['number'] = episode_number
                episodes_infos['title'] = episode_title
                episodes_infos['video'] = episode_video
                episodes_infos['release'] = release_format
                
                episodes_list.append(episodes_infos)

            if not default_source: self.driver.close()

            df_episodes = self.dataframe_create(episodes_list)

            if default_source:
                self.driver.switch_to.window(self.driver.window_handles[1])

            self.episodes_insert(serie_url, season_value, df_episodes)
        
        if season_value == 'all':

            self.driver.get('https://www.imdb.com/title/' + serie_code + '/episodes')

            serie_title = self.wait.until(located((By.CSS_SELECTOR, 'h3[itemprop="name"]')))
            serie_dates = get_wait(serie_title).until(located((By.CLASS_NAME, 'nobr')))
            
            try: conclusion_year = re.sub(r'^\s*\(|\)\s*$', '', serie_dates.text).split('–')[1]
            except: conclusion_year = serie_dates.text

            season_list = self.wait.until(located((By.ID, 'bySeason')))
            season_count = len(get_wait(season_list).until(all_located((By.TAG_NAME, 'option'))))

            if conclusion_year == ' ':
                season_count -= 1
            
            season_current = 0

            for _ in range(season_count):

                try:
                
                    episodes_list = []
                
                    season_current += 1
                
                    self.driver.get(f'https://www.imdb.com/title/' + serie_code + '/episodes?season=' + str(season_current))
                    
                    episodes = self.wait.until(all_located((By.CSS_SELECTOR, 'div[itemprop="episodes"]')))
                    
                    episode_number = 0
                    
                    for episode in episodes:
                        
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        
                        episodes_infos = {'number': '', 'title': '', 'video': '', 'release': ''}
                        
                        episode_number += 1
                        
                        ## Title
                        episode_title = get_wait(episode).until(located((By.CSS_SELECTOR, 'a[itemprop="name"]'))).text
                        
                        ## Release
                        episode_release = get_wait(episode).until(located((By.CLASS_NAME, 'airdate'))).text
                        release_format = datetime.strptime(episode_release.replace('.', ''), "%d %b %Y").strftime("%d/%m/%Y")
                    
                        ## Video
                        episode_video = default_source_url(season_value, episode_number) if default_source else self.get_episode_video(serie_code, season_current, episode_number)
                        
                        episodes_infos['number'] = episode_number
                        episodes_infos['title'] = episode_title
                        episodes_infos['video'] = episode_video
                        episodes_infos['release'] = release_format
                        
                        episodes_list.append(episodes_infos)
                        
                        df_episodes = self.dataframe_create(episodes_list)

                    self.episodes_insert(serie_url, str(season_current), df_episodes)

                    self.driver.switch_to.window(self.driver.window_handles[0])

                except: continue

            self.driver.switch_to.window(self.driver.window_handles[2])
            if not default_source: self.driver.close()

        return ['success', 'Successfully episodes add!']


