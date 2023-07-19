def movie_infos(movies_list):

    import pandas as pd
    import Selenium, get_cover, get_movie_video
    from Selenium import By, Keys
    from Selenium import clickable, located, all_located

    from datetime import datetime
    import time

    driver = Selenium.get_driver()
    wait = Selenium.get_wait(driver)
    actions = Selenium.get_actions(driver)
    
    driver.get('https://www.imdb.com/?ref_=nv_home')
    
    movies = []
    
    for movie in movies_list:
        
        movie_infos = {'title': '', 'categories': [], 'directors': [], 'writers': [], 'release': '', 'production': '', 'country': '', 'synopsis': '', 'cover': '', 'video': '' }
    
        ## Search
        wait.until(clickable((By.ID, 'suggestion-search'))).send_keys(movie)
        actions.send_keys(Keys.ENTER).perform()
        wait.until(clickable((By.XPATH, '/html/body/div[2]/main/div[2]/div[3]/section/div/div[1]/section[2]/div[2]/ul/li[1]'))).click()
        
        code = driver.current_url.split('/')[4]
    
        ## Title
        title = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span'))).text
        movie_infos['title'] = title

        categories = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]')))
        categories_names = Selenium.get_wait(categories, 60).until(all_located((By.CLASS_NAME, 'ipc-chip__text')))
        for category_name in categories_names:
            movie_infos['categories'].append(category_name.text)
            
        synopsis = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]'))).text
        movie_infos['synopsis'] = synopsis
        
        directors = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[1]')))
        directors_names = Selenium.get_wait(directors, 60).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
        for director_name in directors_names:
            movie_infos['directors'].append(director_name.text)

        writers = wait.until(located((By.XPATH, '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[2]/div/ul/li[2]')))
        writers_names = Selenium.get_wait(writers, 60).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
        for writer_name in writers_names:
            movie_infos['writers'].append(writer_name.text)
        
        for _ in range(10):
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(0.5)
        
        release = wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-releasedate"]')))

        release_date = Selenium.get_wait(release, 60).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[0]
        movie_infos['release'] = datetime.strptime(release_date, "%B %d, %Y").strftime("%d/%m/%Y")
        
        country = Selenium.get_wait(release, 60).until(located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item'))).text.split(' (')[1]
        movie_infos['country'] = country.replace(')', '')

        productions = wait.until(located((By.CSS_SELECTOR, 'li[data-testid="title-details-companies"]')))
        productions_names = Selenium.get_wait(productions, 60).until(all_located((By.CLASS_NAME, 'ipc-metadata-list-item__list-content-item')))
        for production_name in productions_names:
            movie_infos['production'] = production_name.text
            break

        movie_infos['cover'] = get_cover.get_cover(title)

        movie_infos['video'] = get_movie_video.get_movie_video(title, code)

        movies.append(movie_infos)

    driver.close()

    data = []

    for movie in movies:
        data.append([
            movie['title'],
            '; '.join(movie['categories']),
            '; '.join(movie['directors']),
            '; '.join(movie['writers']),
            movie['release'],
            movie['production'],
            movie['country'],
            movie['synopsis'],
            movie['cover'],
            movie['video']
        ])

    main_infos = pd.DataFrame(data, columns=['Title', 'Categories', 'Directors', 'Writers', 'Release', 'Production', 'Country', 'Synopsis', 'Cover', 'Video'])

    return main_infos

# print(
#     movie_infos()
# )