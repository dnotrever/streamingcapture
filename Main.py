from os import system

from Selenium import get_driver

driver = get_driver()

system('cls')

messageColors = {
    'others': '\033[1;34m',
    'success': '\033[0;32m',
    'error': '\033[1;31m',
    'info': '\033[36m',
    'detail': '\033[1;90m',
    'reset': '\033[0;0m',
}

others, success, error, info, detail, reset = messageColors.values()

parag = f'\n {others}$~{reset}  '

def message(msg):
    color = success if msg[0] == 'success' else error
    system('cls')
    print(parag + color + msg[1] + reset)
    
def executing(label):
    system('cls')
    print(parag + detail + f'Inserting {label}...' + reset)

def commandline():
    
    option = input(parag).split(' # ')

    if option[0] == 'movies':
        
        movies = option[1].split('; ')
        
        executing('movies')
        
        from Movies import Movies
        msg = Movies(driver).movie_infos(movies)
        
        message(msg)
        
    if option[0] == 'series':
        
        series = option[1].split('; ')
        
        executing('series')
        
        from Series import Series
        msg = Series(driver).serie_infos(series)

        message(msg)

    if option[0] == 'episodes':
        
        query = option[1].split(' % ')

        serie = query[0]
        season = query[1].split(' ')

        try:
            if season[1].lower() == 'y': default_source = True
        except:
            default_source = False

        executing('episodes')
        
        from Episodes import Episodes
        msg = Episodes(driver).episodes_infos(serie, season[0], default_source)
        
        message(msg)
        
    if option[0] == 'clear': system('cls')
    
    if option[0] == 'exit': return
    
    driver.switch_to.window(driver.window_handles[0])
        
    commandline()

commandline()