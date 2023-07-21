from os import system

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
    
    option = input(parag).split(' ')

    if option[0] == 'movies':
        
        movies = input(parag + info + 'Movies: ' + reset).split('; ')
        
        executing('movies')
        
        from Movies import movie_infos
        msg = movie_infos(movies)
        
        message(msg)
        
    if option[0] == 'series':
        
        series = input(parag + info + 'Series: ' + reset).split('; ')
        
        executing('series')
        
        from Series import serie_infos
        msg = serie_infos(series)

        message(msg)

    if option[0] == 'episodes':
        
        serie = input(parag + info + 'Serie: ' + reset)
        season = input(parag + info + 'Season: ' + reset)
        source = input(parag + info + 'Default Source? ' + reset).lower()
        
        executing('episodes')
        
        from Episodes import episodes_infos
        msg = episodes_infos(serie, season, source)
        
        message(msg)
        
    if option[0] == 'clear': system('cls')
    
    if option[0] == 'exit': return
        
    commandline()

commandline()