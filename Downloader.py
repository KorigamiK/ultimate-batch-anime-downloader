from typing import List
from bs4 import BeautifulSoup as bs
import requests
import csv
import os
import wget
import io
from multiprocessing.pool import ThreadPool

def list_str(s):
    return ' '.join(map(str, s))

def to_lower(a):
    return a.lower()

def rem_special(a):
    v=list(a)
    for j,i in enumerate(v):
        if i.isalnum():
            pass
        else:
            v.pop(j)
    return list_str(v)

def check(x,y):
    if rem_special(x)==rem_special(y):
        return True
    else :
        return False
    
def downloader(src_url):
    print('\nGetting Episodes\n')
    src = requests.get(src_url).text
    soup = bs(src, 'lxml')
    try:
        last_page = int(soup.find_all('a', class_="btn btn-flat btn-small")[-2].text)
    except:
        last_page = 1

    # ?page=1

    url = lambda x: (src_url + '?page=' + x)
    episode_urls: List[str] = list()
    titles: List[str] = list()
    final: List[str] = list()

    for i in range(1, last_page + 1):
        source = requests.get(url(str(i))).text
        souper = bs(source, 'lxml')
        episode_urls += souper.find_all('a', class_='episode-meta')
        titles += souper.find_all('div', class_="episode-thumbnail__container")
    print('Found {} episodes'.format(len(titles)))
    k = 1
    # https://yugenani.me/watch/fef088de-e09b-4e07-91c2-c07066ee0c60/

    while True:
        try:
            if input('Want all episodes? y/n: ') != 'y':
                start = int(input('from episode number: ')) - 1
                end = int(input('till episode number: '))
            else:
                start = 0
                end = len(titles)
            break
        except:
            print('Enter correct input and in the specified range')
            
    print('Getting links please wait..\n')

    try:
        for i, j in zip(titles, episode_urls[start:end]):
            final += [[str(k) + ' ' + i.img['title'], 'https://yugenani.me' + j['href']]]
            k += 1
    except Exception:
        print('ERROR: Title or link not found')

    for j, i in enumerate(episode_urls[start:end]):
        souping = bs(requests.get('https://yugenani.me' + i['href']).text, 'lxml')
        try:
            final[j].append(souping.find('a', class_="anime-download")['href'])
        except Exception:
            final[j].append('id not found (server error)')
            print('check {} if it works'.format('https://yugenani.me' + i['href']))

    dow_urls = list()

    for j, i in enumerate(final):
        a = 'https://gogo-stream.com/loadserver.php?id' + i[2].split('id')[-1]
        try:
            soupinger = bs(requests.get(a).text, 'lxml')
            final[j][2] = (
                str(soupinger.find('div', class_="videocontent")).split(';')[-3].split('\n')[-3][:-2].strip()[1:])
        except:
            pass

    def vid_selector(link):
        sauce = bs(requests.get(link).content, 'lxml')
        for i in sauce.find_all('div', class_="dowload"):
            quality = i.text.strip().split("\n")
            if len(quality) == 2:
                g.append(quality[1].strip())

    def get_link(link, opt):
        sauce = bs(requests.get(link).content, 'lxml')
        for i in sauce.find_all('div', class_="dowload"):
            quality = i.text.strip().split("\n")
            if len(quality) == 2:
                if g[opt] == quality[1].strip():
                    ret = i.a['href']
                    if geek == 'y':
                        print(ret)
                    return ret

    geek = input('geek mode? y/n: ')
    g = list()
    # to make g (quality list)
    vid_selector(final[-1][-1])

    print()
    for j, i in enumerate(g):
        print(j, i)
    print()
    
    while True:
        try:
            z = int(input('Enter the quality number (eg: 0, 1, 2, 3 ..): '))
            break
        except:
            print('Please enter the correct integer')
    
    print('Scraping links please wait ...\n')

    for j, i in enumerate(final):
        final[j].pop(1)

    def final_updater():
        for j, i in enumerate(final):
            try:
                sou = requests.get(i[1]).text
            except requests.exceptions.RequestException:
                print('bad url (dead) {} so it will be removed'.format(final[j][1]))
                final.pop(j)
                continue
            if geek == 'y':
                print(j)
            final[j][1] = get_link(i[1], z)

    final_updater()
    
    name = src_url.split('/')[-3]

    with open('{}.csv'.format(name), 'w') as f:
        write = csv.writer(f)
        for i in final:
            write.writerow(i)
            dow_urls.append(i[1])

    print('csv created check folder !')

    def make_dirs():
        if not os.path.exists('{}'.format(name)):
            os.makedirs('{}'.format(name))
        os.chdir('./{}'.format(name))

    def downloader(c):
        make_dirs()
        for i in c:
            wget.download(i, os.getcwd())

    def download_url(link):
        file_name = link.split('token')[0].split('/')[-1][:-1]
        print("downloading: ", file_name)
        r = requests.get(link, stream=True)
        if r.status_code == requests.codes.ok:
            with open(file_name, 'wb') as f:
                for data in r:
                    f.write(data)
        return file_name

    if geek == 'y':
        print(dow_urls)

    if input('download {} now? y/n: '.format(name)) == 'y':
        if input('Want parallel downloads? (Sinificantly faster but no progress bar yet!) y/n: ') == 'y':
            make_dirs()
            results = ThreadPool(5).imap_unordered(download_url, dow_urls)
            for r in results:
                print(r)
        else:
            downloader(dow_urls)


def give_url():
    while True:
        src_inp = input('enter url example (https://yugenani.me/anime/akudama-drive/watch/): ')
        try:
            src_inp.split('/')[-2] == 'watch'
            print(src_inp)
            return src_inp
            break
        except:
            print('Give a correct url (check for /watch/ at the end)')


def use_csv():
    inp_name = input(
        'Enter the full name csv file (otherwise it will wont work): ')
    with io.open('anime_list.csv', 'r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count % 2 == 0:
                if check(str(row[0]), inp_name):
                    print(row[1])
                    return row[1]
                    break
                line_count += 1
            else:
                line_count += 1
        print(f'Processed {line_count // 2} lines.')


def many_anime():
    while True:
        try:
            number = int(input('How many anime do you want?: '))
            break
        except Exception:
            print('Enter correct number')
            
    for i in range(number):
        while True:
            var = use_csv()
            if var == None:
                print('series not found Enter EXACT name')
                pass
            else:
                downloader(var)
                break


def go():
    options = ['Give a specific URL', 'Use the anime_list.csv to get many anime!', 'SEARCH (Coming soon !)\n']
    for j, i in enumerate(options):
        print(j, i)
    while True:
        try:
            begin = int(input('Enter the option number: '))
            break
        except Exception:
            print('Enter correct option! \n')
    if begin == 0:
        downloader(give_url())
        print('\nOMEDETO !!\n')
    elif begin == 1:
        many_anime()
        print('\nOMEDETO !!\n')
    else:
        print('Not implemented yet! Check https://github.com/KorigamiK/ultimate-batch-anime-downloader ')
        go()


go()

