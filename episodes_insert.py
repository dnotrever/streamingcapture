def episodes_insert(serie, season):

    import pandas as pd
    import Selenium
    from Selenium import By, Keys
    from Selenium import clickable, located, all_located
    
    import re, time
    
    serie_url = re.sub(r'\W+', '-', serie.lower())

    driver = Selenium.get_driver()
    wait = Selenium.get_wait(driver)
    actions = Selenium.get_actions(driver)
    
    episodes = pd.read_excel('Episodes.xlsx')
    
    driver.get(f'http://localhost:8000/series')

    # Login
    wait.until(clickable((By.ID, 'email'))).send_keys('')
    wait.until(clickable((By.ID, 'password'))).send_keys('')
    wait.until(clickable((By.CLASS_NAME, 'btn'))).click()
    
    if season != 'all':

        driver.get(f'http://localhost:8000/series/{serie_url}/{season}/episodes-control')
            
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

    driver.close()

    return f'Finished!'

# print(
#     episodes_insert('From', '1')
# )