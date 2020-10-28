from bs4 import BeautifulSoup
import requests
from Downloader import downloader
from tabulate import tabulate

# ____________GogoAnime____________
def getname(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    title = soup.find("meta", property="og:title")["content"].split(" at Go")[0]
    return title


# getname('https://gogoanime.so/category/ore-wo-suki-nano-wa-omae-dake-ka-yo-oretachi-no-game-set')
def search_gogo():
    user_input = input("Enter anime: ")

    url = "https://www2.gogoanime.video//search.html"
    html = requests.get(url, params={"keyword": user_input}).text
    soup = BeautifulSoup(html, "html.parser")
    search_results = soup.select("ul.items > li > p > a")
    headers = ["SlNo", "Title"]
    count = -1
    table = []
    links = []
    for result in search_results:
        count += 1
        entry = [count, result.get("title")]
        link = "https://www2.gogoanime.video" + result["href"]
        table.append(entry)
        links.append(link)
    table = tabulate(table, headers, tablefmt="psql")
    table = "\n".join(table.split("\n")[::-1])
    print(table)
    choice = input("Enter num: [0]: ")
    choice = 0 if choice == "" else int(choice)
    return links[choice]


# ____________yugen____________
def search_yugen(search):
    client = requests.session()
    client.get("https://yugenani.me/anime/akudama-drive/watch/")

    if "csrftoken" in client.cookies:
        # Django 1.6 and up
        csrftoken = client.cookies["csrftoken"]
    else:
        # older versions
        csrftoken = client.cookies["csrf"]
    # print(type(csrftoken))
    response = client.post(
        "https://yugenani.me/api/search/",
        data={"query": correct_format(search)},
        headers={
            "referer": "https://yugenani.me/anime/akudama-drive/watch/",
            "X-CSRFToken": csrftoken,
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    data = dict(response.json())
    parsed_data = eval(data["query"].replace("null", "None"))
    for j, i in enumerate(parsed_data):
        print(j, i["fields"]["title"])
    opt = int(input("enter anime number: "))
    return "https://yugenani.me/anime/" + parsed_data[opt]["fields"]["slug"] + "/watch/"


print("1 download from yugenani?")
print("2 download from goganime?")

if int(input("Enter option number: ")) == 1:
    downloader(search_yugen(input("Enter anime name: ")))
else:
    downloader(search_gogo())
