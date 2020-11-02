from bs4 import BeautifulSoup as bs
import requests
from Downloader import downloader
try:
    from tabulate import tabulate
except:
    import subprocess
    subprocess.run("pip install tabulate",shell=True)
    
# ____________GogoAnime____________
def getname(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    title = soup.find("meta", property="og:title")["content"].split(" at Go")[0]
    return title
def get_gogo_domain():
    try:
        r = requests.get('https://gogoanime.tv')
        if r.status_code != 200:
            raise
        return '.tv'
    except:
        try:
            r = requests.get('https://gogoanime.io')
            if r.status_code != 200:
                raise
            return '.io'
        except:
            r = requests.get('https://gogoanime.so')
            if r.status_code != 200:
                raise
            return '.so'

# getname('https://gogoanime.so/category/ore-wo-suki-nano-wa-omae-dake-ka-yo-oretachi-no-game-set')
def search_gogo():
    user_input = input("Enter anime: ")
    domain_extension = get_gogo_domain()
    url = "https://gogoanime{}/search.html".format(domain_extension)
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
        link = "https://gogoanime{}".format(domain_extension) + result["href"]
        table.append(entry)
        links.append(link)
    table = tabulate(table, headers, tablefmt="psql")
    table = "\n".join(table.split("\n")[::-1])
    print(table)
    choice = input("Enter num: [0]: ")
    choice = 0 if choice == "" else int(choice)
    return links[choice]


# ________________Yugenani_______________
def correct_format(x):
    return x.replace(' ', '+')
def search_yugen(search):
    client = requests.session()
    client.get('https://yugenani.me/anime/akudama-drive/watch/')

    if 'csrftoken' in client.cookies:
        # Django 1.6 and up
        csrftoken = client.cookies['csrftoken']
    else:
        # older versions
        csrftoken = client.cookies['csrf']
    #print(type(csrftoken))
    response = client.post('https://yugenani.me/api/search/', data={"query":correct_format(search)},headers={'referer': 'https://yugenani.me/anime/akudama-drive/watch/',
                                                                                                   'X-CSRFToken':csrftoken,                                                                                               
                                                                                                   'X-Requested-With':'XMLHttpRequest'})
    data= dict(response.json())
    parsed_data = eval(data['query'].replace('null','None'))
    if len(parsed_data) == 0:
        print('Found 0 results for {} (spelling error?)'.format(search))
        return False
    else:
        table = [["S.no", "Anime"]]
        for j,i in enumerate(parsed_data):
            table.append([j,i['fields']['title']])
        print(reverse_table(tabulate(table, headers="firstrow", tablefmt="psql")))
    while True:
        try:
            opt = int(input('enter anime number: '))
            break
        except ValueError:
            print('Please enter a number in the correct range.')
        
    return 'https://yugenani.me/anime/'+parsed_data[opt]['fields']['slug']+'/watch/'
# _____________Driver code_____________
print('1 download from yugenani?')
print('2 download from goganime?')

if int(input('Enter option number: '))== 1:
    print()
    flag = True
    while True:
        flag = search_yugen(input('Enter anime name: '))
        if flag != False :            
            downloader(flag)
            break
        else:
            continue
else:
    downloader(search_gogo())
