import re

dates = ' (2005-2019) '

date2 = re.sub(r'^\s*\(|\)\s*$', '', dates).split('-')[1]

if date2:
    print('ended')
else:
    print('waiting')