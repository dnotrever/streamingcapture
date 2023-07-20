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
serie_insert_url = os.getenv('SERIE_INSERT_URL')

def platform_login():
    
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(serie_insert_url)
    
    user_email = os.getenv('EMAIL')
    user_password = os.getenv('PASSWORD')
    
    wait.until(clickable((By.ID, 'email'))).send_keys(user_email)
    wait.until(clickable((By.ID, 'password'))).send_keys(user_password)
    wait.until(clickable((By.CLASS_NAME, 'btn'))).click()

def get_seasons(serie_code):
    
    driver.get(f'https://www.imdb.com/title/' + serie_code + '/episodes')
    
    season = wait.until(located((By.ID, 'bySeason')))
    episodes = Selenium.get_wait(season).until(all_located((By.TAG_NAME, 'option')))

    return len(episodes)

def get_cover(serie_query):
    
    driver.switch_to.window(driver.window_handles[2])
    
    driver.get(f'https://www.themoviedb.org/search?query=' + serie_query)
    
    # Getting Cover
    cover = wait.until(clickable((By.XPATH, '/html/body/div[1]/main/section/div/div/div[2]/section/div[1]/div/div[1]/div/div[1]/div/a/img'))).get_attribute('src')
    cover = cover.split('/')[6]

    return cover

def dataframe_create(series):
    
    data = []

    for serie in series:
        data.append([
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

    main_infos = pd.DataFrame(data, columns=['Title', 'Categories', 'Creators', 'Seasons', 'Release', 'Production', 'Country', 'Conclusion', 'Synopsis', 'Cover'])

    return main_infos

def serie_insert(series):
    
    driver.switch_to.window(driver.window_handles[1])
        
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
            wait.until(clickable((By.ID, field_id))).send_keys(field_value)

        actions.send_keys(Keys.ENTER).perform()
        
    driver.get(serie_insert_url)

def serie_infos(series):
    
    platform_login()
    
    # TMDB Tab
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[2])
    
    for serie in series:
        
        driver.switch_to.window(driver.window_handles[0])
        
        ## Get Serie Search
        serie_query = re.sub(r'[^a-z0-9 ]', '', serie.lower()).replace(' ', '%20')
        driver.get('https://www.imdb.com/find/?q=' + serie_query + '&ref_=nv_sr_sm')
        
        series_list = []
        serie_infos = {'title': '', 'categories': [], 'creators': [], 'seasons': '', 'release': '', 'production': [], 'country': '', 'conclusion': '', 'synopsis': '', 'cover': ''}
    
        ## Select Serie Title
        find_title = wait.until(located((By.CSS_SELECTOR, 'section[data-testid="find-results-section-title"]')))
        Selenium.get_wait(find_title).until(clickable((By.CLASS_NAME, 'find-title-result'))).click()
        
        serie_code = driver.current_url.split('/')[4]
        
        actions.send_keys(Keys.END).perform()
        time.sleep(1.5)

        ## Title
        title = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span'))).text
        serie_infos['title'] = title

        ## Categories
        categories = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]')))
        categories_names = Selenium.get_wait(categories).until(all_located((By.CLASS_NAME, 'ipc-chip__text')))
        for category_name in categories_names:
            serie_infos['categories'].append(category_name.text)
        
        ## Synopsis
        synopsis = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]'))).text
        serie_infos['synopsis'] = synopsis
        
        ## Creators
        creators = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]')))
        creators_names = Selenium.get_wait(creators).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
        for creator_name in creators_names:
            serie_infos['creators'].append(creator_name.text)
        
        ## Release
        release = wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-releasedate"]')))

        ## Date
        release_date = Selenium.get_wait(release).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[0]
        serie_infos['release'] = datetime.strptime(release_date, "%B %d, %Y").strftime("%d/%m/%Y")
        
        ## Country
        country = Selenium.get_wait(release).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[1]
        serie_infos['country'] = country.replace(')', '')

        ## Productions
        productions = wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-companies"]')))
        productions_names = Selenium.get_wait(productions).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
        for production_name in productions_names:
            serie_infos['production'].append(production_name.text)

        seasons = get_seasons(serie_code)
        cover = get_cover(serie_query)
        
        serie_infos['seasons'] = seasons
        serie_infos['cover'] = cover

        series_list.append(serie_infos)
        
        dataframe = dataframe_create(series_list)
        
        serie_insert(dataframe)

    driver.quit()
    
    return 'Successfully series add!'

# print(
#     serie_infos(['from'])
# )