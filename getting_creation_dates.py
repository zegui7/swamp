from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import requests
import sys
import os

import datetime

import pickle

import time

from collections import defaultdict
from glob import glob

def read_pickle(pickle_path):
    all_elements = []
    with open(pickle_path,'rb') as o:
        try:
            while True:
                all_elements.append(pickle.load(o))
        except:
            pass
    return all_elements

def get_all_authors(channel_dict):
    output = defaultdict(lambda: {'name':'','count':0})
    for video in channel_dict:
        comments = video['comments']
        for comment in comments:
            comment_author = comment['main']['author']
            comment_url = comment['main']['url']
            output[comment_url]['name'] = comment_author
            output[comment_url]['count'] += 1
            for reply in comment['replies']:
                reply_author = reply['author']
                reply_url = reply['url']
                output[reply_url]['name'] = reply_author
                output[reply_url]['count'] += 1

    return output

all_pickle_files = glob('*pkl')

all_author_lists = {
    x:get_all_authors(read_pickle(x)) for x in all_pickle_files}

checked = []
more_than_one = defaultdict(set)
all_authors = set()
for x in all_author_lists:
    for author in all_author_lists[x]:
        more_than_one[author].add(x)
        all_authors.add(author)

more_than_one = {
    x:more_than_one[x] for x in more_than_one if len(more_than_one[x]) > 1}

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--mute-audio")
#chrome_options.add_argument("")

browser = webdriver.Chrome(options=chrome_options)

urls = [x for x in all_authors]

creation_dates = {}
try:
    with open('account_creation_dates.csv') as o:
        for line in o:
            line = line.strip().split(',')
            creation_dates[line[0]] = line[1]
except:
    pass

with open('account_creation_dates.csv','a') as o:
    for url in urls:
        if url not in creation_dates:
            browser.get(url + '/about')
            date_created = browser.find_elements_by_xpath(
                '//yt-formatted-string[@class="style-scope ytd-channel-about-metadata-renderer"]')
            date_created = [x.text for x in date_created]
            try:
                views = [x for x in date_created if 'view' in x][-1]
                views = views.strip().split()[0]
            except:
                views = 'NA'
            try:
                date_created = [x for x in date_created if 'Joined' in x][0]
                date_created = ' '.join(date_created.split()[1:])
            except:
                date_created = 'NA'
            creation_dates[url] = date_created
            string = "{},{},{}\n".format(url,date_created,views)
            o.write(string)
