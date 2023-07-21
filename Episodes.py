import pandas as pd
import time, re, os
from datetime import datetime
from dotenv import load_dotenv

import Selenium
from Selenium import By, Keys
from Selenium import clickable, located, all_located

driver = Selenium.get_driver()
wait = Selenium.get_wait(driver)
actions = Selenium.get_actions(driver)

load_dotenv()
home_url = os.getenv('HOME_URL')
series_url = os.getenv('SERIES_URL')
source_1_series = os.getenv('SOURCE_1_SERIES')
source_2_series = os.getenv('SOURCE_2_SERIES')

def platform_login():

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(home_url)

    user_email = os.getenv('EMAIL')
    user_password = os.getenv('PASSWORD')
    
    wait.until(clickable((By.ID, 'email'))).send_keys(user_email)
    wait.until(clickable((By.ID, 'password'))).send_keys(user_password)
    wait.until(clickable((By.CLASS_NAME, 'btn'))).click()

def get_episode_video(serie_code, season, number):

    driver.switch_to.window(driver.window_handles[2])
    
    ## Seasons
    seasons_container = wait.until(all_located((By.CSS_SELECTOR, 'form[method="post"]')))
    
    number_pad = str(number).zfill(2)
    video = source_2_series + serie_code + '-' + str(season) + '-' + str(number)

    try:

        episodes_button = Selenium.get_wait(seasons_container[int(season)-1]).until(all_located((By.TAG_NAME, 'button')))
        
        for episode in episodes_button:
            if number_pad in episode.text:
                driver.execute_script('arguments[0].click();', episode)
                video = wait.until(located((By.XPATH, '/html/body/div[1]/iframe'))).get_attribute('src')
                break
            
        if len(driver.window_handles) > 3:
            for num in range(len(driver.window_handles) - 3):
                driver.switch_to.window(driver.window_handles[3])
                driver.close()
                
    except: pass
    
    print('\n')
    print(number_pad)
    print(video)
        
    return video

def dataframe_create(episodes):
    
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

def episodes_insert(serie_url, season, episodes, season_current=''):

    driver.switch_to.window(driver.window_handles[1])

    if season != 'all':

        driver.get(series_url + serie_url + '/' + season + '/episodes-control')
            
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
                    wait.until(clickable((By.ID, field_id))).send_keys(field_value)

                if index < len(episodes) - 1:
                    wait.until(clickable((By.ID, 'add-episode'))).click()
                
                actions.send_keys(Keys.END).perform()
            
        wait.until(clickable((By.CSS_SELECTOR, 'button[type="submit"]'))).click()

    if season == 'all':
            
        driver.get(series_url + serie_url + '/' + str(season_current) + '/episodes-control')
            
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
                    wait.until(clickable((By.ID, field_id))).send_keys(field_value)

                if index < len(episodes) - 1:
                    wait.until(clickable((By.ID, 'add-episode'))).click()
                
                actions.send_keys(Keys.END).perform()
            
    insert_btn = wait.until(located((By.CSS_SELECTOR, 'button[type="submit"]')))
    driver.execute_script('arguments[0].click();', insert_btn)

def episodes_infos(serie, season_value, default_source='yes'):
    
    default_source_url = lambda season_value, number: source_2_series + serie_code + '-' + season_value + '-' + str(number)
    
    serie_url = re.sub(r'[^\w]+', '-', serie.lower())

    platform_login()
    
    if default_source != 'yes':

        ## Video Tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[2])
        driver.get(source_1_series + serie_url + '/')
        
        try:
            Selenium.get_wait(driver, 5).until(located((By.CLASS_NAME, 'movie-details')))
        except:
            driver.close()
            default_source = 'yes'

    driver.switch_to.window(driver.window_handles[0])

    ## Get Serie Search
    serie_query = re.sub(r'[^a-z0-9 ]', '', serie.lower()).replace(' ', '%20')
    driver.get('https://www.imdb.com/find/?q=' + serie_query + '&ref_=nv_sr_sm')

    ## Select Serie Title
    find_title = wait.until(located((By.CSS_SELECTOR, 'section[data-testid="find-results-section-title"]')))
    Selenium.get_wait(find_title).until(clickable((By.CLASS_NAME, 'find-title-result'))).click()
    
    serie_code = driver.current_url.split('/')[4]
    
    if season_value != 'all':
        
        episodes_list = []
        
        driver.get(f'https://www.imdb.com/title/' + serie_code + '/episodes?season=' + season_value)
        
        episodes = wait.until(all_located((By.CSS_SELECTOR, 'div[itemprop="episodes"]')))

        number = 0
        
        for episode in episodes:

            driver.switch_to.window(driver.window_handles[0])
            
            episodes_infos = {'number': '', 'title': '', 'video': '', 'release': ''}
            
            number += 1

            ## Title
            title = Selenium.get_wait(episode).until(located((By.CSS_SELECTOR, 'a[itemprop="name"]'))).text
            
            ## Release
            release = Selenium.get_wait(episode).until(located((By.CLASS_NAME, 'airdate'))).text
            release_format = datetime.strptime(release.replace('.', ''), "%d %b %Y").strftime("%d/%m/%Y")

            ## Video
            video = default_source_url(season_value, number) if default_source == 'yes' else get_episode_video(serie_code, season_value, number)

            episodes_infos['number'] = number
            episodes_infos['title'] = title
            episodes_infos['video'] = video
            episodes_infos['release'] = release_format
            
            episodes_list.append(episodes_infos)

        df_episodes = dataframe_create(episodes_list)

        episodes_insert(serie_url, season_value, df_episodes)
    
    if season_value == 'all':

        driver.get('https://www.imdb.com/title/' + serie_code + '/episodes')

        season_select = wait.until(located((By.ID, 'bySeason')))
        episodes_options = Selenium.get_wait(season_select).until(all_located((By.TAG_NAME, 'option')))
        
        season_current = 0
        
        for _ in range(len(episodes_options)):
            
            episodes_list = []
            
            driver.switch_to.window(driver.window_handles[0])
            
            try:
                
                season_current += 1
            
                driver.get(f'https://www.imdb.com/title/' + serie_code + '/episodes?season=' + str(season_current))
                
                episodes = wait.until(all_located((By.CSS_SELECTOR, 'div[itemprop="episodes"]')))
                
                number = 0
                
                for episode in episodes:
                    
                    driver.switch_to.window(driver.window_handles[0])
                    
                    episodes_infos = {'number': '', 'title': '', 'video': '', 'release': ''}
                    
                    number += 1
                    
                    ## Title
                    title = Selenium.get_wait(episode).until(located((By.CSS_SELECTOR, 'a[itemprop="name"]'))).text
                    
                    ## Release
                    release = Selenium.get_wait(episode).until(located((By.CLASS_NAME, 'airdate'))).text
                    release_format = datetime.strptime(release.replace('.', ''), "%d %b %Y").strftime("%d/%m/%Y")
                
                    ## Video
                    video = default_source_url(season, number) if default_source else get_episode_video(serie_code, season_current, number)
                    
                    episodes_infos['number'] = number
                    episodes_infos['title'] = title
                    episodes_infos['video'] = video
                    episodes_infos['release'] = release_format
                    
                    episodes_list.append(episodes_infos)
                    
                    df_episodes = dataframe_create(episodes_list)
                    
                episodes_insert(serie_url, season, df_episodes, season_current, season_current)
                        
            except: continue

    driver.quit()
    
    return ['success', 'Successfully episodes add!']


# print(
#     episodes_infos('prison break', '4', 'no')
# )