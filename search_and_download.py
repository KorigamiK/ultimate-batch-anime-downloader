from bs4 import BeautifulSoup as bs
import requests
from Downloader import downloader
try:
    from tabulate import tabulate
except:
    import subprocess
    subprocess.run("pip install tabulate",shell=True)
    
# ____________GogoAnime____________
def getname(sample):
    badname=sample.split('/category/')[-1]
    goodname=' '.join(badname.split('-'))
    return goodname

def reverse_table(table):
    return "\n".join(table.split("\n")[::-1])

#getname('https://gogoanime.so/category/ore-wo-suki-nano-wa-omae-dake-ka-yo-oretachi-no-game-set')
def search_gogo():
    user_input = input('enter anime: ')
    query = "https://ajax.gogocdn.net/site/loadAjaxSearch?keyword={}&id=-1&link_web=https%3A%2F%2Fgogoanime.so%2F"
    get = '+'.join(user_input.split(' '))
    a = query.format(get).split(' ')
    soup = bs(requests.get(a[0]).content,'lxml')
    search_elements=list()
    table = [["S.no", "Anime"]]
    for j,i in enumerate(soup.find('div',class_='\\"thumbnail-recent_search\\"').find_all('a')):
        badurl='/'.join(str(i['href']).split('\\/'))
        goodurl=badurl.split('"')[1][:-1]
        search_elements.append([getname(goodurl), goodurl])
        table.append([j, getname(goodurl)])
    print(reverse_table(tabulate(table, headers="firstrow", tablefmt="psql")))
    opt = int(input('Enter the anime number: '))
    return search_elements[opt][1]


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
