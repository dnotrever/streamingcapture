import pandas as pd
import time
from datetime import datetime

def df_create(episodes_list):
    
    data = []

    for episode in episodes_list:
        data.append([
            episode['number'],
            episode['title'],
            episode['video'],
            episode['release'],
        ])

    main_infos = pd.DataFrame(data, columns=['Number', 'Title', 'Video', 'Release'])

    return main_infos
    
def episodes_infos(serie, season):

    import Selenium
    from Selenium import By, Keys
    from Selenium import clickable, located, all_located
    from episodes_insert import episodes_insert

    driver = Selenium.get_driver()
    wait = Selenium.get_wait(driver)
    actions = Selenium.get_actions(driver)
    
    driver.get('https://www.imdb.com/')

    # Search
    wait.until(clickable((By.ID, 'suggestion-search'))).send_keys(serie)
    actions.send_keys(Keys.ENTER).perform()
    wait.until(clickable((By.XPATH, '/html/body/div[2]/main/div[2]/div[3]/section/div/div[1]/section[2]/div[2]/ul/li[1]'))).click()  
    
    code = driver.current_url.split('/')[4]
    
    episodes_list = []
    
    if season != 'all':
        
        driver.get(f'https://www.imdb.com/title/{code}/episodes?season={season}')
        
        episodes = wait.until(all_located((By.CSS_SELECTOR, 'div[itemprop="episodes"]')))
        
        number = 0
        
        for episode in episodes:
            
            episodes_infos = {'number': '', 'title': '', 'video': '', 'release': ''}
            
            number += 1
            
            title = Selenium.get_wait(episode, 15).until(located((By.CSS_SELECTOR, 'a[itemprop="name"]'))).text
            
            release = Selenium.get_wait(episode, 15).until(located((By.CLASS_NAME, 'airdate'))).text
            release_format = datetime.strptime(release.replace('.', ''), "%d %b %Y").strftime("%d/%m/%Y")
            
            episodes_infos['number'] = number
            episodes_infos['title'] = title
            episodes_infos['video'] = f'https://autoembed.to/tv/imdb/{code}-{season}-{number}'
            episodes_infos['release'] = release_format
            
            episodes_list.append(episodes_infos)
        
        df_create(episodes_list).to_excel('Episodes.xlsx', index=False, header=True)
        
        episodes_insert(serie, season)
    
    if season == 'all':

        driver.get(f'https://www.imdb.com/title/{code}/episodes?season=1')
        
        season_select = wait.until(located((By.ID, 'bySeason')))
        episodes_options = Selenium.get_wait(season_select, 15).until(all_located((By.TAG_NAME, 'option')))
        
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
                    
                    title = Selenium.get_wait(episode, 15).until(located((By.CSS_SELECTOR, 'a[itemprop="name"]'))).text
                    
                    release = Selenium.get_wait(episode, 15).until(located((By.CLASS_NAME, 'airdate'))).text
                    release_format = datetime.strptime(release.replace('.', ''), "%d %b %Y").strftime("%d/%m/%Y")
                
                    episodes_infos['number'] = number
                    episodes_infos['title'] = title
                    episodes_infos['video'] = f'https://autoembed.to/tv/imdb/{code}-{num+1}-{number}'
                    episodes_infos['release'] = release_format
                    
                    episodes_list.append(episodes_infos)
                    
            except: continue
            
    driver.close()

print(
    episodes_infos('from', '2')
)