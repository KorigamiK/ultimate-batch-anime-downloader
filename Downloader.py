from multiprocessing.pool import ThreadPool
from typing import List
import subprocess
import sys
import os
import io


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
exit_val = False

try:
    from bs4 import BeautifulSoup as bs
except Exception:
    install('bs4')
    exit_val = True

try:
    import requests
except Exception:
    install('requests')
    exit_val = True

try:
    import csv
except Exception:
    install('csv')
    exit_val = True


try:
    import wget
except Exception:
    install('wget')
    exit_val = True

    
if exit_val:
    print('\n\nFinished installing the required modules, please restart the script.')
    print('exitig...')
    exit()


version = 3.5

def version_check(x):
    global cur_ver
    soup = bs(
        requests.get(
            "https://github.com/KorigamiK/ultimate-batch-anime-downloader/tags"
        ).content,
        "html.parser",
    )
    cur_ver = float(
        soup.find(
            "h4", class_="flex-auto min-width-0 pr-2 pb-1 commit-title"
        ).a.text.strip()
    )
    return cur_ver == x


def check_ver():
    ans = input("Check for a new version ? y/n: ")
    if ans == "y":
        if version_check(version):
            print("You're on the latest version ! ")
        else:
            print(
                "\n !! Version {} is now available !!\n download it from: \nhttps://github.com/KorigamiK/ultimate-batch-anime-downloader/releases \n".format(
                    cur_ver
                )
            )


def list_str(s):
    return " ".join(map(to_lower, s))


def to_lower(a):
    return a.lower()


def rem_special(a):
    v = list(a)
    for j, i in enumerate(v):
        if not i.isalnum():
            v.pop(j)
    return list_str(v)


def check(x, y):
    return rem_special(x) == rem_special(y)


def downloader(src_url):
    geek = input("geek mode? y/n: ")
    if geek == "y":
        print(src_url)
    print("Getting Episodes\n")
    src = requests.get(src_url).text
    soup = bs(src, "html.parser")
    episode_urls: List[str] = list()
    titles: List[str] = list()
    final: List[str] = list()
    dow_urls = list()
    g = list() #quality list

    def vid_selector(link):
        sauce = bs(requests.get(link).content, "html.parser")
        for i in sauce.find_all("div", class_="dowload"):
            quality = i.text.strip().split("\n")
            if len(quality) == 2:
                g.append(quality[1].strip())

    def get_link(link, opt):
        sauce = bs(requests.get(link).content, "html.parser")
        for i in sauce.find_all("div", class_="dowload"):
            quality = i.text.strip().split("\n")
            if len(quality) == 2:
                if g[opt] == quality[1].strip():
                    ret = i.a["href"]
                    if geek == "y":
                        print(ret)
                    if ret:
                        return ret
                    else:
                        print("quality {} not available for one episode".format(opt))
                        return "This quality does not exist on the server"
                    
    if "yugenani" in src_url:

        try:
            last_page = int(
                soup.find_all("a", class_="btn btn-flat btn-small")[-2].text
            )
        except Exception:
            last_page = 1

        # ?page=1

        url = lambda x: (src_url + "?page=" + x)

        for i in range(1, last_page + 1):
            source = requests.get(url(str(i))).text
            souper = bs(source, "html.parser")
            episode_urls += souper.find_all("a", class_="episode-meta")
            titles += souper.find_all("div", class_="episode-thumbnail__container")
        print("Found {} episodes".format(len(titles)))

        # https://yugenani.me/watch/fef088de-e09b-4e07-91c2-c07066ee0c60/

        while True:
            try:
                if input("Want all episodes? y/n: ") == "y":
                    start = 0
                    end = len(titles)
                else:
                    start = int(input("from episode number: ")) - 1
                    end = int(input("till episode number: "))
                break
            except Exception:
                print("Enter correct input and in the specified range")

        print("Getting links please wait..\n")
        k = start + 1
        try:
            for i, j in zip(titles, episode_urls[start:end]):
                final += [
                    [str(k) + " " + i.img["title"], "https://yugenani.me" + j["href"]]
                ]
                k += 1
        except Exception:
            print("ERROR: Title or link not found")

        for j, i in enumerate(episode_urls[start:end]):
            souping = bs(
                requests.get("https://yugenani.me" + i["href"]).text, "html.parser"
            )
            try:
                final[j].append(souping.find("a", class_="anime-download")["href"])
            except Exception:
                final[j].append("id not found (server error)")
                print("check {} if it works".format("https://yugenani.me" + i["href"]))

        for j, i in enumerate(final):
            a = "https://gogo-stream.com/loadserver.php?id" + i[2].split("id")[-1]
            try:
                soupinger = bs(requests.get(a).text, "html.parser")
                final[j][2] = (
                    str(soupinger.find("div", class_="videocontent"))
                    .split(";")[-3]
                    .split("\n")[-3][:-2]
                    .strip()[1:]
                )
            except Exception:
                pass

        # to make g (quality list)
        try:
            vid_selector(final[-1][-1])
        except Exception:
            print("There should atleast be 1 episode selected")
            return

        print()
        for j, i in enumerate(g):
            print(j, i)
        print()

        while True:
            try:
                z = int(input("Enter the quality number (eg: 0, 1, 2, 3 ..): "))
                if z >= 0 and z < len(g):
                    break
                else:
                    print("Enter correct option in range !")
            except Exception:
                print("Please enter the correct integer")

        print("Scraping links please wait ...\n")

        for j, i in enumerate(final):
            final[j].pop(1)

        def final_updater():
            for j, i in enumerate(final):
                try:
                    sou = requests.get(i[1]).text
                except requests.exceptions.RequestException:
                    print("bad url (dead) {} so it will be removed".format(final[j][1]))
                    final.pop(j)
                    continue
                if geek == "y":
                    print(j)
                final_link = get_link(i[1], z)
                if not final_link:
                    print(
                        "The selected quality is not availabe for episode {}".format(
                            final[j][0]
                        )
                    )
                final[j][1] = final_link

        final_updater()
        name = src_url.split("/")[-3]
    # ______________________end of yugenani specific______________________

    elif "gogoanime" in src_url:

        def gogo_get(link):
            # get gogo-stream from episode page
            soup = bs(requests.get(link).content, "html.parser")
            return soup.find("li", class_="dowloads").a["href"]

        def gogo_urls_get(link, print_length=False):
            soup = bs(requests.get(link).content, "html.parser")
            last = int(soup.find("a", class_="active")["ep_end"])
            if print_length:
                print("Found {} episodes\n".format(last))
            else:
                anime_name = link.split("/")[-1]
                template = "https://gogoanime.so/" + anime_name + "-episode-"
                next_url = (template + str(i) for i in range(1, last + 1))
                return next_url

        gogo_urls_get(src_url, True)
        start = 0
        end = 1

        def get_range():
            nonlocal start, end
            a = input("want all episodes? y/n: ")

            start = None
            end = None

            if a == "n":
                try:
                    start = int(input("from episode number: ")) - 1
                    end = int(input("till episode number: "))
                except Exception:
                    print("Please carefully enter you input")
                    get_range()
                    
            return a == "n"
            
        def make_final_gogo():
            ans = get_range()
            print("Getting links please wait... ")
            for i in list(gogo_urls_get(src_url))[start:end]:
                dow_link = gogo_get(i)
                final.append(
                    ["ep {}".format("".join(dow_link.split("+")[-1])), dow_link]
                )

            if geek == "y":
                print(final)

        make_final_gogo()

        # To make g(quality list)
        try:
            vid_selector(final[-1][-1])
        except Exception:
            print("There should at least be 1 episode selected")
            return

        def input_quality():
            print()
            for j, i in enumerate(g):
                print(j, i)
            print()

            while True:
                try:
                    z = int(input("Enter the quality number (eg: 0, 1, 2, 3 ..): "))
                    if z >= 0 and z < len(g):
                        break
                    else:
                        print("Enter correct option in range !")
                except Exception:
                    print("Please enter the correct integer")
            print("Scraping links please wait ...\n")
            return z

        option = input_quality()

        for j, i in enumerate(final):
            final[j][1] = get_link(i[1], option)
            if not final[j][1]:
                print(
                    "The selected quality is not available for {}".format(final[j][0])
                )
        name = src_url.split("/")[-1]
    #  __________________________End of Gogo anime specific__________________________
    else:
        print("That website is not supported!")
        return

    with open("{}.csv".format(name), "w") as f:
        write = csv.writer(f)
        for i in final:
            write.writerow(i)
            dow_urls.append(i[1])

    print("csv created check folder !")

    def make_dirs():
        if not os.path.exists("{}".format(name)):
            os.makedirs("{}".format(name))
        os.chdir("./{}".format(name))

    def downloader(c):
        make_dirs()
        for i in c:
            wget.download(i, os.getcwd())

    def download_url(link):
        file_name = link.split("token")[0].split("/")[-1][:-1]
        print("downloading: ", file_name)
        r = requests.get(link, stream=True)
        if r.status_code == requests.codes.ok:
            with open(file_name, "wb") as f:
                for data in r:
                    f.write(data)
        return file_name

    if geek == "y":
        print(dow_urls)

    # check dead links
    for j, i in enumerate(dow_urls):
        if not i:
            dow_urls.pop(j)

    if input("download {} now? y/n: ".format(name)) == "y":
        if (
            input(
                "Want parallel downloads? (Significantly faster but no progress bar yet!) y/n: "
            )
            == "y"
        ):
            make_dirs()
            results = ThreadPool(5).imap_unordered(download_url, dow_urls)
            for r in results:
                print(r)
        else:
            downloader(dow_urls)


# ________________From url(0)_____________________________
def give_url():
    while True:
        src_inp = input(
            "Enter url example\n(https://yugenani.me/anime/akudama-drive/watch/)\n(https://gogoanime.so/category/black-clover-tv)\nor -1 to go back : "
        )
        try:
            if src_inp == "-1":
                go()
                return
            src_inp.split("/")[-2] == "watch"
            print(src_inp)
            return src_inp
        except Exception:
            print("Give a correct url (check for /watch/ at the end for yugenani)")


# ___________________Use Csv(1)________________________________________
def use_csv():
    inp_name = input("Enter the full name csv file (otherwise it will wont work): ")
    with io.open("anime_list.csv", "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count % 2 == 0:
                if check(str(row[0]), inp_name):
                    print(row[1])
                    return row[1]
            line_count += 1
        print(f"Processed {line_count // 2} lines.")


def many_anime():
    while True:
        try:
            number = input("How many anime do you want?\nor -1 to go back: ")
            if number == "-1":
                go()
                return
            number = int(number)
            break
        except Exception:
            print("Enter correct number")

    for i in range(number):
        while True:
            var = use_csv()
            if var:
                downloader(var)
                break
            else:
                print("series not found Enter EXACT name")

# ______________Search(2)_______________________


def getname(sample):
    badname = sample.split("/category/")[-1]
    goodname = " ".join(badname.split("-"))
    return goodname


# getname('https://gogoanime.so/category/ore-wo-suki-nano-wa-omae-dake-ka-yo-oretachi-no-game-set')
def search_prep():
    global found_url
    user_input = input("Enter anime name or -1 to go back: ")
    if user_input == "-1":
        go()
        return
    query = "https://ajax.gogocdn.net/site/loadAjaxSearch?keyword={}&id=-1&link_web=https%3A%2F%2Fgogoanime.so%2F"
    get = "+".join(user_input.split(" "))
    a = query.format(get).split(" ")
    soup = bs(requests.get(a[0]).content, "html.parser")
    search_elements = list()
    for j, i in enumerate(
        soup.find("div", class_='\\"thumbnail-recent_search\\"').find_all("a")
    ):
        badurl = "/".join(str(i["href"]).split("\\/"))
        goodurl = badurl.split('"')[1][:-1]
        search_elements.append([getname(goodurl), goodurl])
        print(j, getname(goodurl))
    while True:
        try:
            opt = int(input("Enter -1 to search again or\nEnter the anime number: "))
            break
        except ValueError:
            print("Enter correct number in range !")
            
    if opt == -1:
        print("OK")
        search_prep()
    elif opt >= 0 and opt < len(search_elements):
#            print(search_elements[opt][1])
        found_url = search_elements[opt][1]
        return None
    else:
        print("Enter correct option in range !")
        search_prep()

def go():
    options = [
        "Give a specific URL (Gogoanime or Yugenani)",
        "Use the anime_list.csv to get many anime! (Including somewhat fuzzy search !)",
        "Search for an anime directly",
        "Use this if option 2 doesn't show the desired results\n"
    ]
    for j, i in enumerate(options):
        print(j, i)
    while True:
        try:
            begin = int(input("Enter the option number: "))
            break
        except Exception:
            print("Enter correct option! \n")
    if begin == 0:
        downloader(give_url())
        print("\nOMEDETO !!\n")
    elif begin == 1:
        many_anime()
        print("\nOMEDETO !!\n")
    elif begin == 2:
        while True:
            try:
                search_prep()
                print()
                break
            except AttributeError:
                print("Sorry, found no results for that (check spelling?)")
        downloader(found_url)
    elif begin == 3:
        import search_and_download
        print("\nOMEDETO !!\n")
    else:
        print(
            "\nNot implemented yet! Check \nhttps://github.com/KorigamiK/ultimate-batch-anime-downloader\n "
        )
        go()


if __name__ == "__main__":
    check_ver()
    print()
    go()
