from gwt import *

days = 3

get_data_from_gwt(10, days)
data = get_data_stored(days)
res = analyze(data)

file_path = os.path.join(os.path.dirname(__file__), 'response.txt')
with open(file_path, 'w') as f:
    f.write(res.text)

output()
