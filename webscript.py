import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime
import random
import time
random.seed(datetime.datetime.now())


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
# US english
LANGUAGE = "en-US,en;q=0.5"

site_url = ""


def get_soup(url,paras=None):
    """Constructs and returns a soup using the HTML content of `url` passed"""
    # initialize a session
    session = requests.Session()
    # set the User-Agent as a regular browser
    session.headers['User-Agent'] = USER_AGENT
    # request for english content (optional)
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    # make the request
    try:
        if url=='/':
            html = session.get(site_url)
        else:
            html = session.get(url)        
    except Exception as e:
        return "[-] bad link ->"+url+" error-> "+str(e)

    # return the soup
    return BeautifulSoup(html.content, "html.parser")


def get_all_tables(soup):
    """Extracts and returns all tables in a soup object"""
    return soup.find_all("table")

def get_table_headers(table):
    """Given a table soup, returns all the headers"""
    headers = []
    for th in table.find("tr").find_all("th"):
        headers.append(th.text.strip())
    return headers


def get_table_rows(table):
    """Given a table, returns all its rows"""
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = []
        # grab all td tags in this table row
        tds = tr.find_all("td")
        if len(tds) == 0:
            # if no td tags, search for th tags
            # can be found especially in wikipedia tables below the table
            ths = tr.find_all("th")
            for th in ths:
                cells.append(th.text.strip())
        else:
            # use regular td tags
            for td in tds:
                cells.append(td.text.strip())
        rows.append(cells)
    return rows

def save_as_csv(table_name, headers, rows):
    pd.DataFrame(rows, columns=headers).to_csv(f"{table_name}.csv")

def save_as_json(table_name, headers, rows):
    pd.DataFrame(rows, columns=headers).to_json(f"{table_name}.json",orient='records')


#links (a href) found on the page
def getInternalLinks(bsObj, includeUrl):
    internalLinks = []
    #Finds all links that begin with a "/"
    for link in bsObj.findAll("a", href=re.compile("^(/|.*"+includeUrl+")")):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in internalLinks:
                internalLinks.append(link.attrs['href'])
    return internalLinks
# all links from https://urlextractor.net/
def extract_url(url):
    url_site = "https://urlextractor.net/"
    paras = {"target_url":url,'href':1,'meta':1,'link_type':'internal','extract':'Extract Links'}
    header = {'User-Agent':USER_AGENT}
    from urllib.parse import urlencode
    html = requests.get(url_site, params=urlencode(paras),headers=header)
    return BeautifulSoup(html.content, "html.parser")


def main(url,isInternalLink=False):
    if not isInternalLink:
        # get the soup
        soup = get_soup(url)
        if 'bad link' in soup:
            print(soup)
        if 'table' not in soup.find("table"):
            print("[-] Url do not have a table")
            exit()
        createFile(soup,url)
    else:
        extactor = extract_url(url)
        # print(extactor)
        links = getInternalLinks(extactor,'fallingrain')
        print("[+] Links ",links)
        for link in links:
            # print(links)
            print("[+] compling -",link)
            time.sleep(25)
            soup = get_soup(link)
            if 'bad link' in soup:
                print(soup)
            if  not soup.find("table"):
                continue
            createFile(soup,link)
            print("[+] done compling")




def createFile(soup,urlName):
        # extract all the tables from the web page
        tables = get_all_tables(soup)
        print("table---------> ",str(urlName))

        print(f"[+] Found a total of {len(tables)} tables.")
        # iterate over all tables
        for i, table in enumerate(tables, start=1):
            # get the table headers
            headers = get_table_headers(table)
            # get all the rows of the table
            rows = get_table_rows(table)
            # save table as csv file
            filename = re.sub(r'(www\.|https://|http://|\.htm|\.html|\.com|\.net|\.org|\/)', '',urlName)
            table_name = f"table-{i}-{filename}"
            print(f"[+] Saving {table_name}")
            if(len(rows)>0):
                save_as_csv(table_name, headers, rows)
                save_as_json(table_name, headers, rows)

if __name__ == "__main__":
    try:
        # global site_url
        site_url = "http://fallingrain.com/world/GH/"
        main(site_url,True)
    except Exception as e:
        print("Error {e}",e)
        exit(1)
    