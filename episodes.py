import time
import re
import os
import traceback
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from custom_traceback import traceback_formatted

from selenium_core import sc

class Episodes:
    
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv('BASE_URL')
        self.series_url = os.getenv('SERIES_URL')
        self.source_1_series = os.getenv('SOURCE_1_SERIES')
        self.source_2_series = os.getenv('SOURCE_2_SERIES')
    
    def close_spam_tabs(self, actived_tabs):

        if sc.tab('count') > actived_tabs:
            for _ in range(sc.tab('count') - actived_tabs):
                sc.tab(actived_tabs, 'select')
                sc.close()

    def platform_login(self):

        sc.tab(1)
        
        sc.get(self.base_url + '/login')
    
        user_email = os.getenv('EMAIL')
        user_password = os.getenv('PASSWORD')
        
        sc.element('id', 'email').send_keys(user_email)
        sc.element('id', 'password').send_keys(user_password)
        sc.click('class', 'btn')

    def get_episode_video(self, serie_code, season_value, episode_number):

        # sc.tab(2)
        
        video = self.source_1_series + serie_code + '-' + str(season_value) + '-' + str(episode_number)
        alternative = ''

        # try:

        #     seasons_container = sc.element('selector', 'form[method="post"]', 'all')
        
        #     number_pad = str(episode_number).zfill(2)
            
        #     episodes_button = sc.element('tag', 'button', 'all', seasons_container[int(season_value)-1])
            
        #     for episode in episodes_button:
        #         if number_pad in re.findall(r'\d{2}', episode.text):
        #             sc.click('none', episode)
        #             alternative = sc.element('xpath', '/html/body/div[1]/iframe').get_attribute('src')
        #             break
                    
        # except: 
            
        #     pass
            
        # self.close_spam_tabs(3)
        
        return video, alternative

    def dataframe_create(self, episodes):
        
        data = []

        for episode in episodes:
            data.append([
                episode['number'],
                episode['title'],
                episode['video'],
                episode['alternative'],
                episode['release'],
            ])

        main_infos = pd.DataFrame(data, columns=['Number', 'Title', 'Video', 'Alternative', 'Release'])

        return main_infos

    def episodes_insert(self, serie_url, season, episodes):

        sc.tab(1, 'select')

        sc.get(self.series_url + serie_url + '/' + season + '/episodes-control')
            
        for index, row in episodes.iterrows():

            if index < len(episodes):
                    
                mapping = {
                    'Title': f'title_{index}',
                    'Video': f'video_{index}',
                    'Alternative': f'alternative_{index}',
                    'Release': f'released_{index}',
                }

                for key, value in mapping.items():

                    field_id = value
                    field_value = row[key]

                    if pd.isna(field_value): field_value = ''

                    input_field = sc.element('id', field_id)
                    
                    input_field.clear()
                    input_field.send_keys(field_value)

                if index < len(episodes) - 1:
                    sc.click('id', 'add-episode')
                
        episode_form = sc.element('class', 'App_episodesControlForm')
        sc.click('none', sc.element('selector', 'button[type="submit"]', 'one', episode_form))

    def episodes_infos(self, serie_title, season_value, seasons_number=0):
        
        try:
            
            if sc.tab('count') == 1:
                self.platform_login()

            sc.tab(0, 'select')
            
            if season_value != 'all':
            
                ## Get Serie Search
                serie_query = re.sub(r'[^a-z0-9 ]', '', serie_title.lower()).replace(' ', '%20')
                sc.get('https://www.imdb.com/find/?q=' + serie_query + '&ref_=nv_sr_sm')
            
                ## Select Serie Title
                search_serie_title = sc.element('selector', 'section[data-testid="find-results-section-title"]')
                sc.element('class', 'find-title-result', 'one', search_serie_title).click()

            serie_code = sc.current_url().split('/')[4]

            serie_url = re.sub(r'[^\w]+', '-', serie_title.lower())

            if season_value != 'all':
                
                episodes_list = []
                
                episode_number = 0
                
                sc.get(f'https://www.imdb.com/title/' + serie_code + '/episodes?season=' + season_value)
                
                season_list  = sc.element('class', 'jPRxOq')
                episodes = sc.element('class', 'bGxjcH', 'all', season_list)
                
                for episode in episodes:
                    
                    sc.tab(0, 'select')
                    
                    episodes_infos = {'number': '', 'title': '', 'video': '', 'alternative': '', 'release': ''}
                    
                    episode_number += 1

                    ## Title
                    episode_title = (sc.element('class', 'bglHll', 'one', episode).text).split(' ∙ ')[1]
                    
                    ## Release
                    episode_release = sc.element('class', 'jEHgCG', 'one', episode).text
                    release_format = datetime.strptime(episode_release, "%a, %b %d, %Y").strftime("%d/%m/%Y")

                    ## Video
                    episode_video = self.get_episode_video(serie_code, season_value, episode_number)

                    episodes_infos['number'] = episode_number
                    episodes_infos['title'] = episode_title
                    episodes_infos['video'], episodes_infos['alternative'] = episode_video
                    episodes_infos['release'] = release_format
                    
                    episodes_list.append(episodes_infos)

                df_episodes = self.dataframe_create(episodes_list)

                self.episodes_insert(serie_url, season_value, df_episodes)
            
            if season_value == 'all':
                    
                season_count = seasons_number
                
                season_current = 0

                for _ in range(season_count):

                    try:
                    
                        episodes_list = []
                    
                        season_current += 1
                    
                        sc.get(f'https://www.imdb.com/title/' + serie_code + '/episodes?season=' + str(season_current))
                        
                        season_list  = sc.element('class', 'jPRxOq')
                        episodes = sc.element('class', 'bGxjcH', 'all', season_list)
                        
                        episode_number = 0
                        
                        for episode in episodes:
                            
                            sc.tab(0, 'select')
                            
                            episodes_infos = {'number': '', 'title': '', 'video': '', 'alternative': '', 'release': ''}
                            
                            episode_number += 1
                            
                            ## Title
                            episode_title = (sc.element('class', 'bglHll', 'one', episode).text).split(' ∙ ')[1]
                           
                            ## Release
                            episode_release = sc.element('class', 'jEHgCG', 'one', episode).text
                            release_format = datetime.strptime(episode_release, "%a, %b %d, %Y").strftime("%d/%m/%Y")
                                                    
                            ## Video
                            episode_video = self.get_episode_video(serie_code, season_current, episode_number)
                            
                            episodes_infos['number'] = episode_number
                            episodes_infos['title'] = episode_title
                            episodes_infos['video'], episodes_infos['alternative'] = episode_video
                            episodes_infos['release'] = release_format
                            
                            episodes_list.append(episodes_infos)
                            
                            df_episodes = self.dataframe_create(episodes_list)

                        self.episodes_insert(serie_url, str(season_current), df_episodes)

                        sc.tab(0, 'select')

                    except:
                        
                        continue

            return ['success', 'Successfully episodes add!']

        except:
            
            return ['error', traceback_formatted(traceback.format_exc())]

