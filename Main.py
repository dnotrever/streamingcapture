from os import system

system('cls')

option = input('\n$~  ').split(' ')

if option[0] == 'movies':
    movies = input('\n$~  Movies:  ').split('; ')
    from Movies import movie_infos
    print(movie_infos(movies))

if option[0] == 'series':
    series = input('\n$~  Series:  ').split('; ')
    from Series import serie_infos
    print(serie_infos(series))

if option[0] == 'episodes':
    pass
