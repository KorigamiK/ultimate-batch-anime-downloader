import requests
from bs4 import BeautifulSoup as bs
import csv
import io

src_url = r"https://yugenani.me/discover/"
cont = requests.get(src_url).content
soup = bs(cont, "html.parser")
# print(soup.prettify())

last = soup.find_all("a", class_="btn btn-flat btn-small")[-2].text


def url(a):
    for i in range(1, int(a)):
        src = src_url + "?page=" + str(i)
        yield (src)


next_url = url(last)
with io.open("anime_list.csv", "w", encoding="utf-8") as f:
    write = csv.writer(f)
    for i in range(int(last)):
        cur_url = next(next_url)
        souper = bs(requests.get(cur_url).content, "html.parser")
        for j in souper.find_all("a", class_="anime-meta"):
            l = list()
            l.append(j.find("div", class_="anime-data").span.text)
            l.append("https://yugenani.me" + j["href"] + "watch/")
            write.writerow(l)
        print(1)
