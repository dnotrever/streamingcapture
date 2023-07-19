from os import system

system('cls')

option = input('\n$~  ').split(' ')

if option[0] == 'movies':
    pass

if option[0] == 'series':
    series = input('\n$~  Series: ').split('; ')
    from Series import serie_infos
    print(serie_infos(series))

if option[0] == 'episodes':
    pass
