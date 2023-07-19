def get_movie_video(movie, code):

    import Selenium
    from Selenium import By, Keys
    from Selenium import clickable

    driver = Selenium.get_driver()
    wait = Selenium.get_wait(driver)
    actions = Selenium.get_actions(driver)

    driver.get('https://tugaflix.best/filmes/') 
    
    wait.until(clickable((By.ID, 'search'))).send_keys(movie)

    actions.send_keys(Keys.ENTER).perform()

    try:

        wait.until(clickable((By.XPATH, '/html/body/div[1]/form/div[6]/div[1]'))).click()

        wait.until(clickable((By.XPATH, '/html/body/div[1]/center/form/button'))).click()

        wait.until(clickable((By.XPATH, '/html/body/div[1]/div[4]/a[1]'))).click()

        video = wait.until(clickable((By.XPATH, '/html/body/iframe'))).get_attribute('src')

        return video
    
    except: return f'https://autoembed.to/movie/imdb/{code}'
    
    finally: driver.close()

# print(
#     get_movie_video('Avengers Endgame')
# )