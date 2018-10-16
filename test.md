```
import requests
headers = {'User-Agent': 'Chrome/69.0.3497.100'}
url_591 = "https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=2&searchtype=1&region=1"
res = requests.get(url_591, headers=headers).json()
total_page = int(res["records"].replace(",", ""))

all_data = []
for i in range(0, int(total_page/30)+1):
    url = "https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=2&searchtype=1&region=1&firstRow={}&totalRows={}".format(i*30, total_page)
    res = requests.get(url, headers=headers).json()
    all_data.extend(res["data"]["data"])
    print("{:3d}\t{:4d}".format(i, len(all_data)))
```


# test
```
import pandas as pd
df = pd.DataFrame(all_data)
df.groupby("user_id")['id'].count().reset_index(name='count').sort_values(['count'], ascending=False).head()
df[(df.user_id == 1318377)].filter(items=['address', 'area', "price"])
```
