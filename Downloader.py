from bs4 import BeautifulSoup as bs
import requests
import csv
import os
import wget

src_url=input('enter url example (https://yugenani.me/anime/akudama-drive/watch/): ')
src=requests.get(src_url).text
soup=bs(src,'lxml')

try:
    last_page=int(soup.find_all('a',class_="btn btn-flat btn-small")[-2].text)
except:
    last_page=1

# ?page=1

url=lambda x: (src_url + '?page='+ x)
episode_urls=list()
titles=list()
final=list()

for i in range(1,last_page + 1):
    source=requests.get(url(str(i))).text
    souper=bs(source,'lxml')
    episode_urls+=souper.find_all('a',class_='episode-meta')
    titles+=souper.find_all('div',class_="episode-thumbnail__container")
print(len(episode_urls),len(titles))    
k=1
# https://yugenani.me/watch/fef088de-e09b-4e07-91c2-c07066ee0c60/

start=int(input('from episode number: '))-1
end=int(input('till episode number: '))

try:
    for i , j in zip(titles,episode_urls[start:end]):
        final+=[[str(k)+' '+i.img['title'], 'https://yugenani.me'+j['href']]]
        k+=1
except:
    print('error')

for j,i in enumerate(episode_urls[start:end]):
    souping=bs(requests.get('https://yugenani.me'+i['href']).text,'lxml')
    try:
        final[j].append(souping.find('a',class_="anime-download")['href'])
    except:
        final[j].append('id not found (server error)')
        print('check {} if it works'.format('https://yugenani.me'+i['href']))

dow_urls=list()

for j,i in enumerate(final):
    a='https://gogo-stream.com/loadserver.php?id'+i[2].split('id')[-1]
    try:
        soupinger=bs(requests.get(a).text,'lxml')    
        final[j][2]=(str(soupinger.find('div', class_="videocontent")).split(';')[-3].split('\n')[-3][:-2].strip()[1:])
    except:
        pass
for j,i in enumerate(final):
    final[j].pop(1)

g=['(HDP - mp4)','(360P - mp4)','(720P - mp4)','(1080P - mp4)']
print(g)

z=int(input('the index number from the list (eg: 1, 2, 3 ..): '))

geek=input('geek mode? y/n')

for j,i in enumerate(final):
    try:
        sou=requests.get(i[1]).text
        souper=bs(sou,'lxml')
        for k in souper.find_all('div', class_="dowload"):
            #get all available formats from here
            try:
                if g[z]==k.text.split('\n')[1].strip():
                    if geek=='y':
                        print(k.text.split('\n')[1].strip())
                        print(k.a['href'])
                    final[j][1]=k.a['href']
            except:
                pass
    except:
        pass

name=src_url.split('/')[-3]

with open('{}.csv'.format(name),'w') as f:
    write=csv.writer(f)
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
print(dow_urls)

if input('download now? y/n: ')=='y':
    downloader(dow_urls)
