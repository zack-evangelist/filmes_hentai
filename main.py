# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from time import sleep
import re
import json

url = 'https://filmeshentai.com/'
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5)

def login():
    driver.get('https://filmeshentai.com/acesso')
    sleep(1)
    button_user_area = driver.find_element(By.XPATH, '/html/body/header/div[1]/div/label[2]')
    button_user_area.click()
    sleep(1)
    input_email = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[1]/form/fieldset[1]/input')
    input_email.send_keys(data['email'])
    input_password = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[1]/form/fieldset[2]/input')
    input_password.send_keys(data['password'])
    button_submit = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[1]/form/span/button')
    button_submit.click()
    sleep(1)
    driver.get('https://filmeshentai.com/')

def get_subtitled_movies_links():
    pages_moovies_agregators = ['https://filmeshentai.com/filmes-legendados']

    driver.get('https://filmeshentai.com/filmes-legendados')
    next_pages = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/ul/div/ul')
    next_pages_links = next_pages.find_elements(By.TAG_NAME, 'a')
    for i in next_pages_links:
        link = i.get_attribute("href")
        pages_moovies_agregators.append(link)

    moovies_links = []
    
    for link in pages_moovies_agregators:
        driver.get(link)
        div_all_moovies = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]')
        moovies_divs = div_all_moovies.find_elements(By.CLASS_NAME, 'item')

        for i in moovies_divs:
            link_moovie = i.find_element(By.TAG_NAME, 'a').get_attribute("href")
            moovies_links.append(link_moovie)
            # print(link_moovie)

    return moovies_links

def get_moovies(moovies_pages_links):
    moovies = []

    def get_video_url(player_link):
        pattern = r"(https://videos\.[A-Za-z0-9_-]+\.[netcom]{3}/[A-Za-z0-9_-]+\.mp4)"
        matches = re.findall(pattern, player_link)
        # print(matches[0])
        if matches:
            link = matches[0]
            return link
        else:
            print(f'error: {player_link}')
            return None

    for moovie_page in moovies_pages_links:
        driver.get(moovie_page)
        info_div = driver.find_element(By.XPATH, '/html/body/section[1]/div/div[1]')
        title = info_div.find_element(By.TAG_NAME, 'h1').text.strip()
        description = info_div.find_element(By.TAG_NAME, 'h2').text.strip()
        div_cover = driver.find_element(By.CLASS_NAME, 'capa')
        image = div_cover.find_element(By.TAG_NAME, 'img').get_attribute("src")
        page = BeautifulSoup(driver.page_source, 'html.parser')
        ifr = page.find('iframe')
        print(image)
        moovie_link = get_video_url(ifr['src'])
        if moovie_link is not None:
            moovies.append({
                'title': title,
                'description': description,
                'link': moovie_link,
                'image': image
            })
        else:
            print(f'error: {moovie_page}')

    return {
        'moovies':moovies
    }

def make_json(moovies):
    with open('moovies.json', 'w', encoding="utf8") as f:
        json.dump(moovies, f, indent=4, ensure_ascii=False)

def load_json(filepath):
    with open(filepath, 'r', encoding="utf8") as f:
        moovies = json.load(f)
    return moovies

def download_videos(moovies):
    def download(moovie):
        with open(f'moovies/{moovie["title"]}.mp4', 'wb') as file:
            file.write(requests.get(moovie['link']).content)

    moovies_objs = moovies['moovies']
    with tqdm(total=len(moovies_objs), desc='downloading files') as progress_bar:
        progress_bar.colour='blue'
        for moovie in moovies_objs:
            progress_bar.desc=f'download {moovie["title"]}'
            download(moovie)
            progress_bar.update(1)

if __name__ == '__main__':
    data = load_json('./data.json')
    login()
    moovies_pages_links = get_subtitled_movies_links()
    moovies = get_moovies(moovies_pages_links)
    make_json(moovies)
    moovies = load_json('moovies.json')
    download_videos(moovies)