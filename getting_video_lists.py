# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import exceptions
import requests
import sys
import os
from threading import Thread
from queue import Queue

import argparse

import datetime

import pickle

import time

def scroll_down(driver):
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

        # Wait to load the page.
        time.sleep(2.5)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

def check_trial_bs():
    trial_bs = browser.find_elements_by_xpath(
        '//ytd-button-renderer[@id="dismiss-button"]'
    )

    trial_bs = [x for x in trial_bs if x.text.upper() == 'SKIP TRIAL']
    if len(trial_bs) > 0:
        trial_bs[0].click()

def thumbs_to_int(thumbs):
    try:
        if thumbs[-1] == 'K':
            return int(float(thumbs[:-1]) * 1e3)
        elif thumbs[-1] == 'M':
            return int(float(thumbs[:-1]) * 1e6)
        elif thumbs[-1] == 'B':
            return int(float(thumbs[:-1]) * 1e9)
        else:
            return int(thumbs)
    except:
        return ''

link_store = {
    r"DefesaDeHonra":'https://www.youtube.com/channel/UCsXXjOpQqJek_CnbXQZtkag',
    r"CHEGA":"https://www.youtube.com/channel/UC-Wo4qU-W0CNd-9Q23GIWKg",
    r"CDS-PP":"https://www.youtube.com/channel/UC6lFx2F-zcUN240ebh0MXqQ",
    r"Iniciativa Liberal":"https://www.youtube.com/channel/UC4XjoC521Qpo6Pr_tOfDXRw",
    r"JoaoTilly":"https://www.youtube.com/channel/UCbJ3e750S4ZyW4ZFhXDQ62w",
    r"JoaoMacedo(TalkAboutemPortugues)":"https://www.youtube.com/channel/UCqoXOOuzmq2GYWOUBMM3Y0g",
    r"NoticiasViriato":"https://www.youtube.com/channel/UCKJ8sfWrx779vAb6f8Z5I4g",
    r"GoncaloSousa":"https://www.youtube.com/channel/UCHrcuJEgZhrCXhDT5W14_xQ",
    r"MarioMachado":"https://www.youtube.com/channel/UCM-l2zrrDh1ioNSJ7W2vIrw",
    r"GatoPolitico":"https://www.youtube.com/channel/UCGLIfziYOn6NgSx5iv1_uUw",
    r"PSD":"https://www.youtube.com/user/PPDPSDNACIONAL",
    r"PNR":"https://www.youtube.com/user/canalnacionalista"
}

def main():

    link = link_store[curr_swamp]
    print(curr_swamp)

    browser.get(link)

    video_element = browser.find_elements_by_xpath(
        "//paper-tab/div[@class='tab-content style-scope paper-tab']")
    video_element = [x for x in video_element if x.text == 'VIDEOS'][0]
    video_element.click()
    time.sleep(1)
    
    all_videos = browser.find_elements_by_xpath(
        "//div[@class='style-scope ytd-grid-video-renderer']/div[@id='details']")

    O = []
    if os.path.exists('video_urls/{}.pkl'.format(curr_swamp)):
        with open('video_urls/{}.pkl'.format(curr_swamp),'rb') as o:
            while True:
                try:
                    O.append(pickle.load(o))
                except EOFError:
                    break

        A = O[0][0]
        B = all_videos[0].text.split('\n')[0]
        if A == B:
            return None
    
    all_done_urls = [x[1] for x in O]

    print("\tScrolling down...")
    scroll_down(browser)

    # grabbing all video urls
    all_videos = browser.find_elements_by_xpath(
        "//div[@class='style-scope ytd-grid-video-renderer']/div[@id='details']")
    check_dates = True
    
    with open('video_urls/{}.pkl'.format(curr_swamp),'wb') as OUTPUT:
        i = 0
        for x in all_videos:
            try:
                i += 1
                title = x.find_element_by_id("video-title")
                title_text = title.text
                print('\tCurrent video: {} ({}/{})'.format(title_text,i,len(all_videos)))

                if check_dates == True:
                    date = x.find_elements_by_xpath(
                        ".//span[@class='style-scope ytd-grid-video-renderer']")
                    date = date[1].text
                    if any([x in date for x in ['day','second','minute','hour']]):
                        date = date
                    else:
                        date = '>1 week'
                        check_dates = False
            
                else:
                    date = '>1 week'
                url = title.get_attribute('href')
                if url in all_done_urls:
                    break
                info = [title_text,url,date]

                pickle.dump(info,OUTPUT,
                            protocol=pickle.HIGHEST_PROTOCOL)

            except exceptions.StaleElementReferenceException as e:
                pass 
        for info in O:
            pickle.dump(info,OUTPUT,
                        protocol=pickle.HIGHEST_PROTOCOL)

parser = argparse.ArgumentParser(description='Fetch videos.')
parser.add_argument('--idx',dest='idx',
                    type=str,
                    default='list',
                    help='ID of the channel.')
parser.add_argument('--headless',dest='headless',
                    action='store_true',
                    help='Should chromedriver be run in headless mode?')
args = parser.parse_args()

if args.idx == 'list':
    for n in link_store:
        print('{}'.format(n.encode()),link_store[n])

else:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    if args.headless == True:
        chrome_options.add_argument("--headless")

    browser = webdriver.Chrome(options=chrome_options)
    idx = int(args.idx)
    curr_swamp = [x for x in link_store.keys()][idx]

    try:
        os.makedirs('video_urls')
    except:
        pass

    swamp_list = main()
    browser.quit()
