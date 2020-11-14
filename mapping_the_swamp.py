# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import requests
import sys
import os
from threading import Thread
from queue import Queue

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
        time.sleep(1.2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

def scrape_comment_thread(c):

    def scrape_comment(ytd_comment_thread_renderer):

        click_more = ytd_comment_thread_renderer.find_elements_by_xpath(
            ".//span[@class='more-button-exp style-scope ytd-comment-renderer']")
        click_more = [x for x in click_more if x.text == 'Read more']
        if len(click_more) > 0:
            browser.execute_script(
                "window.scrollTo(0, {});".format(click_more[-1].location['y'] - 200))
            click_more[0].click()
        author = ytd_comment_thread_renderer.find_element_by_xpath(
            './/a[@id="author-text"]')
        main_text = ytd_comment_thread_renderer.find_element_by_xpath(
            './/yt-formatted-string[@id="content-text"]')
        vote_count = ytd_comment_thread_renderer.find_element_by_xpath(
            './/span[@id="vote-count-middle"]')
        time_ago = ytd_comment_thread_renderer.find_element_by_xpath(
            './/a[@class="yt-simple-endpoint style-scope yt-formatted-string"]')

        url = author.get_attribute('href')
        return author,main_text,vote_count,url,time_ago

    reply_list = []


    reply_button = c.find_elements_by_xpath(
        './/yt-formatted-string[@class="style-scope ytd-button-renderer"]')
    reply_button = [x for x in reply_button if 'repl' in x.text]
    if len(reply_button) > 0:
        check_trial_bs()
        reply_button = reply_button[0]
        browser.execute_script("window.scrollTo(0, {});".format(reply_button.location['y']-200))
        ActionChains(browser).move_to_element(
            reply_button)
        ActionChains(browser).click(reply_button).perform()
        replies_found = False
        all_comments = False
        while replies_found == False:
            reply_general = c.find_element_by_xpath('.//div[@id="replies"]')
            replies = reply_general.find_elements_by_xpath('.//ytd-comment-renderer')
            if len(replies) > 0:
                replies_found = True

        time.sleep(0.5)

        check_more_replies_success = False
        while check_more_replies_success == False:
            try:
                check_more_replies = reply_general.find_elements_by_xpath(
                    './/yt-formatted-string[@class="style-scope yt-next-continuation"]')

                check_more_replies = [
                    x for x in check_more_replies if 'repl' in x.text
                ]

                check_more_replies_success = True
            except:
                pass

        if len(check_more_replies) > 0:
            while all_comments == False:
                if len(check_more_replies) > 0:
                    browser.execute_script(
                        "window.scrollTo(0, {});".format(check_more_replies[-1].location['y'] - 200))

                    check_more_replies[-1].click()
                    keep_going = True
                    curr_size = browser.execute_script(
                        "return document.documentElement.scrollHeight")
                    time.sleep(1.0)
                    while keep_going:
                        new_size = browser.execute_script(
                            "return document.documentElement.scrollHeight")
                        if curr_size == new_size:
                            keep_going = False
                        else:
                            curr_size = new_size
                        time.sleep(0.5)
                    check_more_replies = reply_general.find_elements_by_xpath(
                        './/yt-formatted-string[@class="style-scope yt-next-continuation"]')
                    check_more_replies = [
                        x for x in check_more_replies if 'repl' in x.text]
                else:
                    all_comments = True
        replies = reply_general.find_elements_by_xpath('.//ytd-comment-renderer')
        for reply in replies:
            author,main_text,vote_count,url,time_ago = scrape_comment(reply)
            reply_list.append({
                'author':author.text,
                'main_text':main_text.text,
                'vote_count':vote_count.text,
                'url':url,
                'time_ago':time_ago.text
            })

    author,main_text,vote_count,url,time_ago = scrape_comment(c)

    output_dict = {
        'main': {
            'author':author.text,
            'main_text':main_text.text,
            'vote_count':vote_count.text,
            'url':url,
            'time_ago':time_ago.text
        },
        'replies': reply_list
    }

    return output_dict

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

def main(swamp_list):

    def update_info(swamp_list):
        with open(output_name,'wb') as OUTPUT:
            for i,title in enumerate(all_video_url_keys):
                if title in all_video_dates:
                    swamp_list = [x for x in swamp_list if x['title'] != title]
                else:
                    curr = [x for x in swamp_list if x['title'] == title]
                    if len(curr) > 0:
                        pickle.dump(curr[0],OUTPUT,
                                    protocol=pickle.HIGHEST_PROTOCOL)
        return swamp_list

    link = link_store[curr_swamp]

    browser.get(link)

    all_video_urls = {}
    all_video_dates = {}

    check_dates = True
    with open('video_urls/{}.pkl'.format(curr_swamp),'rb') as o:
        try:
            while True:
                title_text,url,date = pickle.load(o)
                if date != '>1 week':
                    all_video_dates[title_text] = date

                all_video_urls[title_text] = url
        except:
            pass

    all_video_url_keys = [x for x in all_video_urls.keys()]
    all_video_url_keys.reverse()

    que = Queue()

    a = Thread(target=lambda q, arg1: q.put(update_info(arg1)),
               args=(que, swamp_list))
    a.start()
    a.join()
    swamp_list = que.get()

    OUTPUT = open(output_name,'ab')

    print("Number of videos already scrapped:",len(swamp_list))

    for i,title in enumerate(all_video_url_keys):
        print('({}/{})'.format(i+1,len(all_video_urls)))
        if title not in [x['title'] for x in swamp_list]:
            url = all_video_urls[title]
            browser.get(url)

            # this is to pause the video
            time.sleep(0.5)
            actions = ActionChains(browser)
            actions.send_keys(Keys.SPACE).perform()

            has_loaded = False
            while has_loaded == False:
                date = browser.find_elements_by_xpath(
                    "//yt-formatted-string[@class='style-scope ytd-video-primary-info-renderer']")
                if len(date) >= 2:
                    has_loaded = True

            date = date[1]
            view_count = browser.find_element_by_xpath(
                "//span[@class='view-count style-scope yt-view-count-renderer']")
            thumbs = browser.find_elements_by_xpath(
                "//yt-formatted-string[@class='style-scope ytd-toggle-button-renderer style-text']")
            thumbs = [thumbs_to_int(x.text) for x in thumbs]

            # delete recommendation bar
            element = browser.find_element_by_xpath(
                '//div[@id="secondary"]')
            browser.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, element)

            init_height = 500
            browser.execute_script(
                "window.scrollTo(0, {});".format(init_height))
            time.sleep(0.5)
            browser.execute_script(
                "window.scrollTo(0, {});".format(init_height+500))
            S = browser.find_element_by_xpath("//ytd-item-section-renderer")
            while S.text == '':
                S = browser.find_element_by_xpath("//ytd-item-section-renderer")

            print('\t',"Scrapping comments...")

            comments = []
            curr = init_height
            keep_going = True
            curr_text = S.text
            last_height = 0
            while keep_going == True:
                n_comments = len(comments)
                curr += int(S.size['height'])
                browser.execute_script("window.scrollTo(0, {});".format(curr))
                time.sleep(0.5)
                curr_height = browser.execute_script("return document.documentElement.scrollHeight")
                if curr_height == last_height:
                    keep_going = False
                else:
                    last_height = curr_height

                comment_objs = browser.find_elements_by_xpath('//ytd-comment-thread-renderer')

                for c in comment_objs[n_comments:]:
                    check_trial_bs()
                    comments.append(scrape_comment_thread(c))

            print('\tNumber of comments found:',len(comments))
            print('\tRecording entries...')

            video_dict = {
                'title':title,
                'date':date.text,
                'view_count':view_count.text,
                'url':url,
                'comments':comments,
                'date_scrapped':datetime.date.today(),
                'thumbs_up':thumbs[0],
                'thumbs_up':thumbs[1]
            }

            pickle.dump(video_dict,OUTPUT,
                        protocol=pickle.HIGHEST_PROTOCOL)

if sys.argv[1] == 'list':
    for n in link_store:
        print('{}'.format(n.encode()),link_store[n])

else:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("window-size=1920,1080")

    browser = webdriver.Chrome(options=chrome_options)
    idx = int(sys.argv[1])
    curr_swamp = [x for x in link_store.keys()][idx]

    output_name = '{}.pkl'.format(curr_swamp)

    if os.path.isfile(output_name):
        with open(output_name,'rb') as o:
            swamp_list = []
            try:
                while True:
                    swamp_list.append(pickle.load(o))
            except EOFError:
                pass

    else:
        swamp_list = []

    swamp_list = main(swamp_list)

    browser.quit()
