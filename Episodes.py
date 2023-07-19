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
serie_url_1 = os.getenv('SERIE_URL_1')
serie_url_2 = os.getenv('SERIE_URL_2')

def platform_login():

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(home_url)

    user_email = os.getenv('EMAIL')
    user_password = os.getenv('PASSWORD')
    
    wait.until(clickable((By.ID, 'email'))).send_keys(user_email)
    wait.until(clickable((By.ID, 'password'))).send_keys(user_password)
    wait.until(clickable((By.CLASS_NAME, 'btn'))).click()

def get_episode_video(season, number):

    driver.switch_to.window(driver.window_handles[2])

    time.sleep(3)
    actions.send_keys(Keys.END).perform()

    ## Seasons
    seasons_container = wait.until(all_located((By.TAG_NAME, 'form')))

    if season != 'all':

        episodes_button = Selenium.get_wait(seasons_container[int(season)-1]).until(all_located((By.TAG_NAME, 'button')))
        
        episodes_button[number-1].click()

        time.sleep(3)
        actions.send_keys(Keys.END).perform()

        video = wait.until(located((By.XPATH, '/html/body/div[1]/iframe'))).get_attribute('src')

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

def episodes_insert(serie, season, episodes):

    driver.switch_to.window(driver.window_handles[1])

    if season != 'all':

        driver.get(series_url + serie + '/' + season + '/episodes-control')
            
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
        
        for num in range(50):
            
            driver.get(f'http://localhost:8000/series/{serie_url}/{num+1}/episodes-control')
                
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

def episodes_infos(serie, season):

    platform_login()

    ## Video Tab
    serie_url = re.sub(r'[^\w]+', '-', serie.lower()) + '/'
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[2])
    driver.get(serie_url_1 + serie_url)

    driver.switch_to.window(driver.window_handles[0])

    ## Get Serie Search
    serie_query = re.sub(r'[^a-z0-9 ]', '', serie.lower()).replace(' ', '%20')
    driver.get('https://www.imdb.com/find/?q=' + serie_query + '&ref_=nv_sr_sm')

    ## Select Serie Title
    find_title = wait.until(located((By.CSS_SELECTOR, 'section[data-testid="find-results-section-title"]')))
    Selenium.get_wait(find_title).until(clickable((By.CLASS_NAME, 'find-title-result'))).click()
    
    serie_code = driver.current_url.split('/')[4]
    
    episodes_list = []
    
    if season != 'all':
        
        driver.get(f'https://www.imdb.com/title/' + serie_code + '/episodes?season=' + season)
        
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
            video = get_episode_video(season, number)

            episodes_infos['number'] = number
            episodes_infos['title'] = title
            episodes_infos['video'] = video
            episodes_infos['release'] = release_format
            
            episodes_list.append(episodes_infos)
        
        if len(driver.window_handles) > 2:
            for num in range(len(driver.window_handles) - 2):
                driver.switch_to.window(driver.window_handles[num+2])
                driver.close()

        dataframe = dataframe_create(episodes_list)
        
        print(dataframe)

        episodes_insert(serie, season, dataframe)
    
    if season == 'all':

        driver.get(f'https://www.imdb.com/title/{code}/episodes?season=1')
        
        season_select = wait.until(located((By.ID, 'bySeason')))
        episodes_options = Selenium.get_wait(season_select).until(all_located((By.TAG_NAME, 'option')))
        
        season_current = 0
        
        for num in range(len(episodes_options)):
            
            try:
                
                season_current += 1
            
                driver.get(f'https://www.imdb.com/title/{code}/episodes?season={season_current}')
                
                episodes = wait.until(all_located((By.CSS_SELECTOR, 'div[itemprop="episodes"]')))
                
                number = 0
                
                for episode in episodes:
                    
                    episodes_infos = {'number': '', 'title': '', 'video': '', 'release': ''}
                    
                    number += 1
                    
                    title = Selenium.get_wait(episode).until(located((By.CSS_SELECTOR, 'a[itemprop="name"]'))).text
                    
                    release = Selenium.get_wait(episode).until(located((By.CLASS_NAME, 'airdate'))).text
                    release_format = datetime.strptime(release.replace('.', ''), "%d %b %Y").strftime("%d/%m/%Y")
                
                    episodes_infos['number'] = number
                    episodes_infos['title'] = title
                    episodes_infos['video'] = f'https://autoembed.to/tv/imdb/{code}-{num+1}-{number}'
                    episodes_infos['release'] = release_format
                    
                    episodes_list.append(episodes_infos)
                    
            except: continue
            
    driver.quit()

print(
    episodes_infos('from', '2')
)