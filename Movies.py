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
movies_url = os.getenv('MOVIES_URL')
source_1_movies = os.getenv('SOURCE_1_MOVIES')
source_2_movies = os.getenv('SOURCE_2_MOVIES')

def platform_login():

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(movies_url + 'insert')

    user_email = os.getenv('EMAIL')
    user_password = os.getenv('PASSWORD')
    
    wait.until(clickable((By.ID, 'email'))).send_keys(user_email)
    wait.until(clickable((By.ID, 'password'))).send_keys(user_password)
    wait.until(clickable((By.CLASS_NAME, 'btn'))).click()

def get_movie_video(movie, movie_code, movie_year):

    driver.switch_to.window(driver.window_handles[3])

    movie_url = re.sub(r'[^\w]+', '-', movie.lower()) + '-' + movie_year + '/'

    try:
        driver.get(source_1_movies + movie_url)

        wait.until(clickable((By.CSS_SELECTOR, 'button[name="play"]'))).click()

        if len(driver.window_handles) > 4:
            for num in range(len(driver.window_handles) - 4):
                driver.switch_to.window(driver.window_handles[num+4])
                driver.close()

        divPlay = wait.until(located((By.CLASS_NAME, 'play')))

        linksPlay = Selenium.get_wait(divPlay).until(all_located((By.CLASS_NAME, 'btn')))

        for link in linksPlay:
            try:
                video = link.get_attribute('href')
                break
            except:
                continue

        return video
    
    except:
        return source_2_movies + movie_code

def get_cover(movie_query):
    
    driver.switch_to.window(driver.window_handles[2])
    
    driver.get(f'https://www.themoviedb.org/search?query=' + movie_query)
    
    # Getting Cover
    cover = wait.until(clickable((By.XPATH, '/html/body/div[1]/main/section/div/div/div[2]/section/div[1]/div/div[1]/div/div[1]/div/a/img'))).get_attribute('src')
    cover = cover.split('/')[6]

    return cover

def dataframe_create(movies):
    
    data = []

    for movie in movies:
        data.append([
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

    main_infos = pd.DataFrame(data, columns=['Title', 'Categories', 'Release', 'Directors', 'Writers', 'Production', 'Country', 'Video', 'Cover', 'Synopsis'])

    return main_infos

def movie_insert(movies):

    driver.switch_to.window(driver.window_handles[1])

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
            wait.until(clickable((By.ID, field_id))).send_keys(field_value)

    actions.send_keys(Keys.ENTER).perform()

    driver.get(movies_url + 'insert')

def movie_infos(movies):

    platform_login()
    
    # TMDB Tab
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[2])

    # Video Tab
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[3])
    
    for movie in movies:

        driver.switch_to.window(driver.window_handles[0])
        
        ## Get Movie Search
        movie_query = re.sub(r'[^a-z0-9 ]', '', movie.lower()).replace(' ', '%20')
        driver.get('https://www.imdb.com/find/?q=' + movie_query + '&ref_=nv_sr_sm')

        movies_list = []
        movie_infos = {'title': '', 'categories': [], 'directors': [], 'writers': [], 'release': '', 'production': [], 'country': '', 'synopsis': '', 'cover': '', 'video': '' }
    
        ## Select Movie Title
        find_title = wait.until(located((By.CSS_SELECTOR, 'section[data-testid="find-results-section-title"]')))
        Selenium.get_wait(find_title).until(clickable((By.CLASS_NAME, 'find-title-result'))).click()

        movie_code = driver.current_url.split('/')[4]

        actions.send_keys(Keys.END).perform()
        time.sleep(2)
    
        ## Title
        title = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span'))).text
        movie_infos['title'] = title

        ## Categories
        categories = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]')))
        categories_names = Selenium.get_wait(categories).until(all_located((By.CLASS_NAME, 'ipc-chip__text')))
        for category_name in categories_names:
            movie_infos['categories'].append(category_name.text)
        
        ## Synopsis
        synopsis = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]'))).text
        movie_infos['synopsis'] = synopsis
        
        ## Directors
        directors = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]')))
        directors_names = Selenium.get_wait(directors).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
        for director_name in directors_names:
            movie_infos['directors'].append(director_name.text)

        ## Writers
        writers = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]')))
        writers_names = Selenium.get_wait(writers).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
        for writer_name in writers_names:
            movie_infos['writers'].append(writer_name.text)

        ## Release
        release = wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-releasedate"]')))

        ## Date
        release_date = Selenium.get_wait(release).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[0]
        movie_infos['release'] = datetime.strptime(release_date, "%B %d, %Y").strftime("%d/%m/%Y")
        
        ## Country
        country = Selenium.get_wait(release).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[1]
        movie_infos['country'] = country.replace(')', '')

        ## Productions
        productions = wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-companies"]')))
        productions_names = Selenium.get_wait(productions).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
        for production_name in productions_names:
            movie_infos['production'].append(production_name.text)

        release_year = movie_infos['release'].split('/')[2]

        video = get_movie_video(title, movie_code, release_year)

        cover = get_cover(movie_query)

        movie_infos['video'] = video
        movie_infos['cover'] = cover

        movies_list.append(movie_infos)
        
        dataframe = dataframe_create(movies_list)
        
        movie_insert(dataframe)

    driver.quit()
    
    return 'Successfully movies add!'

print(
    movie_infos(['avengers endgame', 'forrest gump'])
)