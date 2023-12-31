from os import system

from selenium_core import sc

sc.set_driver()

system('clear')

messageColors = {
    'others': '\033[34m',
    'success': '\033[32m',
    'error': '\033[31m',
    'info': '\033[36m',
    'detail': '\033[90m',
    'reset': '\033[0m',
}

others, success, error, info, detail, reset = messageColors.values()

parag = f'\n {others}$~{reset} '

def message(msg):
    color = success if msg[0] == 'success' else '\n\n' + error
    print(parag + color + msg[1] + reset)
    
def executing(label):
    print(parag + detail + f'Inserting {label}...' + reset)

def commandline():
    
    option = input(parag).split(' # ')

    if option[0] == 'movies':
        
        movies = option[1].split(';')
        
        executing('movies')
        
        from movies import Movies
        msg = Movies().movie_infos(movies)
        
        message(msg)
        
    if option[0] == 'series':
        
        series = option[1].split('; ')
        
        executing('series')
        
        from series import Series
        msg = Series().serie_infos(series)

        message(msg)

    if option[0] == 'episodes':
        
        query = option[1].split(' % ')

        serie = query[0]
        season = query[1]

        executing('episodes')
        
        from episodes import Episodes
        msg = Episodes().episodes_infos(serie, season[0])
        
        message(msg)
        
    if option[0] == 'clear': system('clear')
    
    if option[0] == 'exit': return
    
    sc.tab(0, 'select')
        
    commandline()

commandline()