#!/usr/bin/python
#coding=utf8

import urllib
import urllib2
from bs4 import BeautifulSoup
import sqlite3
import sys
import time

#set default encoding as UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')

#oldcwj@gmail.com

base_url = 'http://www.imdb.com'
film_type = ['Action', 'Animation', 'Comedy', 'Drama', 'Horror', 'Sci-Fi']


def get_html(url1):
    print('get html')
    #伪装浏览器头部
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    req = urllib2.Request(url = url1,headers = headers)
    html = ''
    try:
        html = urllib2.urlopen(req, timeout=30).read()
        #print html
    except:
        print 'timeout'
    return html


def load_film(url, conn, type):
    html = get_html(url)
    if html=='':
        return
    html_soup = BeautifulSoup(html, from_encoding="utf8")
    lister_list = html_soup.find(class_='lister-list')
    # print lister_list
    for item in lister_list.find_all('div', class_='lister-item mode-advanced'):
        # print item
        item_content = item.find('div', class_='lister-item-content')
        film_index = item_content.find('span', class_='lister-item-index unbold text-primary').text
        film_name = item_content.a.text
        film_url = item_content.a['href']
        film_year = item_content.find('span', class_='lister-item-year text-muted unbold').text
        film_year = parse_number(film_year)
        print film_index
        print film_name
        print film_url
        print film_year

        time.sleep(3)

        film_detail_url = base_url + film_url;
        detail_html = get_html(film_detail_url)
        detail_soup = BeautifulSoup(detail_html, from_encoding="utf8")

        # budget
        budget_array = detail_soup.find_all('h4', text='Budget:')
        budget_string = ''
        if len(budget_array) > 0:
            budget_div = budget_array[0].parent.text
            budget_string = budget_div[budget_div.index('Budget:') + 7: budget_div.index('(estimated)')].strip()
            print 'Budget:', budget_string

        # gross
        gross_array = detail_soup.find_all('h4', text='Gross:')
        gross_string = ''
        if len(gross_array) > 0:
            gross_div = gross_array[0].parent.text
            gross_string = gross_div[gross_div.index('Gross:') + 6: gross_div.index('(USA)')].strip()
            print 'Gross:', gross_string

        # Genres
        action = 0; animation = 0; comedy = 0; drama = 0; horror = 0; sci_fi = 0
        genres_array = detail_soup.find_all('h4', text='Genres:')

        if len(genres_array) > 0:
            genres_a = genres_array[0].parent.find_all('a')
            if len(genres_a) > 0:
                for a in genres_a:
                    #print a
                    a_text = a.string.strip()
                    print a_text
                    if a_text == film_type[0]: action = 1
                    if a_text == film_type[1]: animation = 1
                    if a_text == film_type[2]: comedy = 1
                    if a_text == film_type[3]: drama = 1
                    if a_text == film_type[4]: horror = 1
                    if a_text == film_type[5]: sci_fi = 1

        # insert to db(sqlite3)
        if budget_string != '' and gross_string != '' and ('$' in budget_string) and ('$' in gross_string):
            budget = parse_number(budget_string)
            gross = parse_number(gross_string)
            insert_data(conn, film_name, film_url, int(film_year), action, animation, comedy, drama,
                        horror, sci_fi, int(budget), int(gross))


def get_genres(genres):
    if genres in film_type:
        return 1
    return 0

def parse_number(s):
    s = filter(lambda ch: ch in '0123456789', s)
    return s


def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    return conn


def create_table(conn):
    cursor = conn.cursor()
    #cursor.execute('DELETE from films')
    #conn.commit('')

    # 0:action 1:animation 2:comedy 3:drama 4:drama 5:sci-fi
    cursor.execute('''CREATE TABLE films
                 (name       TEXT  PRIMARY KEY   NOT NULL,
                  url        TEXT     NOT NULL,
                  year       INT,
                  action     INT,
                  animation  INT,
                  comedy     INT,
                  drama      INT,
                  horror     INT,
                  sci_fi     INT,
                  budget     REAL,
                  gross      REAL);''')
    conn.commit()


def insert_data(conn, name, url, year, action, animation, comedy, drama, horror, sci_fi, budget, gross):
    try:
        cursor = conn.cursor()
        cursor.execute('''REPLACE INTO films (name, url, year, action, animation, comedy, drama, horror, sci_fi, budget, gross)
                                        VALUES (\'%s\', \'%s\', \'%d\', \'%d\', \'%d\', \'%d\', \'%d\', \'%d\', \'%d\', \'%d\', \'%d\' )'''
                       % (name, url, year, action, animation, comedy, drama, horror, sci_fi, budget, gross))
        conn.commit()
    except:
        print 'insesrt db error'


def exe(type, conn):
    for i in range(1, 10):
        tmp_url = 'http://www.imdb.com/search/title?genres=' + type \
                  + '&sort=user_rating,desc&title_type=feature&num_votes=25000,&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=2406822102&pf_rd_r=0648ZQPSVK4SEM3TFSTR&pf_rd_s=right-6&pf_rd_t=15506&pf_rd_i=top&page=' + bytes(
            i) + '&ref_=adv_nxt'
        print tmp_url
        load_film(tmp_url, conn, type)


def get_all_type_films(conn):
    for type in film_type:
        exe(type, conn)


if __name__ == '__main__':
    print 'begin time:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    conn = connect_db('imdb.db')
    create_table(conn)
    get_all_type_films(conn)
    conn.close()
    print 'end time:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))