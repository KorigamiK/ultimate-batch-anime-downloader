from typing import List
from bs4 import BeautifulSoup as bs
import requests
import csv
import os
import wget
import io

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
            start = int(input('from episode number: ')) - 1
            end = int(input('till episode number: '))
            break
        except:
            print('Enter correct input and in the specified range')

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
    for j, i in enumerate(final):
        final[j].pop(1)

    g: List[str] = ['(HDP - mp4)', '(360P - mp4)', '(720P - mp4)', '(1080P - mp4)']
    print()
    for j,i in enumerate(g):
        print(j,i)

    while True:
        try:
            z = int(input('Enter the index number from the list (eg: 0, 1, 2, 3 ..): '))
            break
        except:
            print('Please enter the correct integer')
            
    geek = input('geek mode? y/n')

    for j, i in enumerate(final):
        try:
            sou = requests.get(i[1]).text
            souper = bs(sou, 'lxml')
            for k in souper.find_all('div', class_="dowload"):
                # get all available formats from here
                try:
                    if g[z] == k.text.split('\n')[1].strip():
                        if geek == 'y':
                            print(k.text.split('\n')[1].strip())
                            print(k.a['href'])
                        final[j][1] = k.a['href']
                except Exception:
                    pass
        except Exception:
            pass

    name = src_url.split('/')[-3]

    with open('{}.csv'.format(name), 'w') as f:
        write = csv.writer(f)
        for i in final:
            write.writerow(i)
            dow_urls.append(i[1])

    print('csv created check folder !')


    def downloader(c):
        if not os.path.exists('{}'.format(name)):
            os.makedirs('{}'.format(name))
        os.chdir('./{}'.format(name))
        for i in c:
            wget.download(i, os.getcwd())


    if geek == 'y':
        print(dow_urls)

    if input('download {} now? y/n: '.format(name)) == 'y':
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
    inp_name=input('Enter the correct name from the csv file (otherwise it will take a long time to show that you have made an error): ')
    with io.open('anime_list.csv','r',encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count%2==0:
                if inp_name==row[0]:
                    print(row[1])
                    return row[1]
                    break
                line_count+=1
            else:
                line_count+=1
        print(f'Processed {line_count//2} lines.')

def many_anime():
    number=int(input('Enter the number of anime you want: '))
    for i in range(number):
        downloader(use_csv())
        
def go():
    options=['Give a specific URL','Use the anime_list.csv to get many anime!','SEARCH (Coming soon !)\n']
    for j,i in enumerate(options):
        print(j,i)
    while True:
        try:
            begin=int(input('Enter the option number: '))
            break
        except Exception:
            print('Enter correct option! \n')
    if begin==0:        
        downloader(give_url())
        print('\nOMEDETO !!\n')
    elif begin==1:
        many_anime()
        print('\nOMEDETO !!\n')
    else:
        print('Not implemented yet! Check https://github.com/KorigamiK/ultimate-batch-anime-downloader ')
        go()
        
go()

