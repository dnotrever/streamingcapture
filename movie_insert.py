def movie_insert():

    import pandas as pd
    import Selenium
    from Selenium import By, Keys
    from Selenium import clickable, located, all_located

    driver = Selenium.get_driver()
    wait = Selenium.get_wait(driver)
    actions = Selenium.get_actions(driver)

    driver.get('http://localhost:8000/movies/insert')

    movies = pd.read_excel('Movies.xlsx')

    wait.until(clickable((By.ID, 'email'))).send_keys('')

    wait.until(clickable((By.ID, 'password'))).send_keys('')

    wait.until(clickable((By.CLASS_NAME, 'btn'))).click()
    
    for _, row in movies.iterrows():
    
        mapping = {
            'Title': 'title',
            'Categories': 'categories',
            'Directors': 'director',
            'Writers': 'writer',
            'Release': 'released',
            'Production': 'production',
            'Country': 'country',
            'Synopsis': 'synopsis',
            'Cover': 'cover',
            'Video': 'video'
        }

        for key, value in mapping.items():
            field_id = value
            field_value = row[key]
            if pd.isna(field_value): field_value = ''
            wait.until(clickable((By.ID, field_id))).send_keys(field_value)

        actions.send_keys(Keys.ENTER).perform()
        
        wait.until(clickable((By.CLASS_NAME, 'btn'))).click()

    driver.close()

    return f'Finished!'

# print(
#     movie_insert()
# )