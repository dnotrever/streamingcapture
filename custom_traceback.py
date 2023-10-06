def traceback_formatted(traceback):
    index = traceback.find('Stacktrace:')
    return traceback[:index] if index != -1 else traceback