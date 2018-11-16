# import requests
# import time
#
# old_time = time.time()
# requests.get('https://en.wikipedia.org/wiki/Web_scraping')
# print(time.time() - old_time)
a = {"a":1,"b":2}
b={"a":2,"c":3}
a.update(b)
print(a)