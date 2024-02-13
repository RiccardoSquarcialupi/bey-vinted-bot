from selenium import webdriver
import multiprocessing
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import system, getcwd, remove, path as _path
import os
from numpy import mean
from discord_webhook import DiscordWebhook, DiscordEmbed
from time import sleep, time
from json import load, dump
import random, string
from colorama import Fore, init
from requests import get
from pypresence import Presence
from pyshorteners import Shortener

# ----- colorama settings -----
c = Fore.LIGHTCYAN_EX
w = Fore.LIGHTWHITE_EX

# ----- banner -----
banner = f"""

                  )                  (         )                  (                       )            
   (           ( /(                  )\ )   ( /(    *   )         )\ )            (    ( /(     *   )  
 ( )\   (      )\())        (   (   (()/(   )\()) ` )  /(   (    (()/(          ( )\   )\())  ` )  /(  
 )((_)  )\    ((_)\   ___   )\  )\   /(_)) ((_)\   ( )(_))  )\    /(_))   ___   )((_) ((_)\    ( )(_)) 
((_)_  ((_)  __ ((_) |___| ((_)((_) (_))    _((_) (_(_())  ((_)  (_))_   |___| ((_)_    ((_)  (_(_())  
 | _ ) | __| \ \ / /       \ \ / /  |_ _|  | \| | |_   _|  | __|  |   \         | _ )  / _ \  |_   _|  
 | _ \ | _|   \ V /         \ V /    | |   | .` |   | |    | _|   | |) |        | _ \ | (_) |   | |    
 |___/ |___|   |_|           \_/    |___|  |_|\_|   |_|    |___|  |___/         |___/  \___/    |_|    
                                                                                                       
"""

# <-----  file reader ----->
def write_file(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as f:
        data = f.write(data)
    return data


# <----- json file reader ----->
def read_json(file_path: str) -> dict:
    with open(file_path, 'r') as json_file:
        data = load(json_file)
    return data


# <----- json file writer ----->
def write_json(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as json_file:
        dump(data, json_file)


# <-----  json file cleaner ----->
def json_cleaner(json_path):
    json_data = read_json(f"{getcwd()}\\assets\\{json_path}")
    json_data.clear()
    json_data.update({})
    json_file = write_json(f"{getcwd()}\\assets\\{json_path}", json_data) 

    system('cls')
    print(f"""\n{banner}\n {c}[{w}INFO{c}]{w} {json_path} has been cleaned succesfully !""")
    sleep(2)


# <----- random letters gen ----->
def lettergen(lenght):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(int(lenght)))


# <----- brand converter ----->
def brand_converter(bid):
    json_data = read_json(f"{getcwd()}\\assets\\brands.json")
    for brand in json_data:
        if bid == str(brand):
            return json_data[bid]
        else:
            pass
    return f"Unlisted brand ({bid})"


# <----- item type converter ----->
def item_type_converter(iid):
    json_data = read_json(f"{getcwd()}\\assets\\item_type.json")
    for item_id in json_data:
        if iid == str(item_id):
            return json_data[iid]
        else:
            pass
    return f"Unlisted item ({iid})"

# <----- size converter ----->
def size_converter(size):
    json_data = read_json(f"{getcwd()}\\assets\\sizes.json")
    for s in json_data:
        if size == s:
            return json_data[size]
        else:
            pass 
        
# <----- remove duplicate ----->
def remove_duplicate(list):
    return [x for i, x in enumerate(list) if x not in list[:i]]

# <----- get settings ----->
def get_settings():
    json_data = read_json(f"{getcwd()}/assets/settings.json")
    return json_data["Item"], json_data["Margin"], json_data["Explored_pages"], json_data["Webhook"]

def info_getter(link):
    options1 = webdriver.FirefoxOptions()
    options1.add_argument('-headless')
    driver = webdriver.Firefox(options=options1)
    driver.get(link)
    try:
        wait = WebDriverWait(driver, 10)
        imgParent = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='item-photo-1--img']")))
        img = imgParent.get_attribute('src')
        desc = driver.find_element(By.CSS_SELECTOR, "span.web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format").text
    except Exception as e:
        driver.close()
        return img, "No description found..."
    driver.close()
    return img, desc
# <----- webhook sender ----->
def webhook_sender(item, webhook_link):
    try:
        webhook = DiscordWebhook(
                url=webhook_link,
                username="Vingod")
        embed = DiscordEmbed(title=item[0], color='FF1F1F')
        
        image, desc = info_getter(item[2])
        desc1 = desc.lower().split(" ")
        word_list = read_json(f"{getcwd()}\\assets\\plastic.json")
        word_list = word_list["beyblade_words"]
        found_words = []
        found_words = [word for word in word_list if word in desc1]

        # Find words from the JSON list inside the input string
        if(bool(found_words)):
            n = len(found_words)
            embed.set_image(image)
            embed.add_embed_field(name='Price :dollar:', value=item[1].replace(" prezzo\xa0:", "" + '€'))
            embed.add_embed_field(name='Product Link :link:', value=shortlink(item[2]), inline=True)
            embed.add_embed_field(name='Description :label:', value=found_words[0]+" - " + desc, inline=True)
            embed.set_author(name='RiccardoSquarcialupi',
                            icon_url='https://avatars.githubusercontent.com/u/44367261?v=4',
                            url='https://github.com/RiccardoSquarcialupi')
            embed.set_footer(text='Let it RIP!!!')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
        else:
            print(found_words)
    except Exception as e:
            e.with_traceback()


# <----- webhook checker ----->
def webhook_checker(webhook_link):
    try:
        resp = get(webhook_link)
        if resp.status_code != 200:
            return "Invalid"
        else:
            return "Valid"
    except Exception as e: 
        return "Invalid"
    
    
# <----- link builder ----->
def link_builder(count):
    link = "https://www.vinted.it/catalog?search_text=beyblade%20plastic&brand_ids[]=270688&brand_ids[]=114196&brand_ids[]=330038&brand_ids[]=65554&brand_ids[]=165516&brand_ids[]=281034&order=newest_first&page=" + str(count) + "'"
    return link
    
    
# <----- progress bar ----->
def progressbar(banner, w, bar):
    system("cls")
    print(f"\n{banner}\n {w}{bar}")

def shortlink(link):
    s = Shortener()
    return s.tinyurl.short(link)
    
# <----- bot ----->
print(banner)
# bot settings

##TODO infinite cycle with time check

items_list = []
final_list = []
price_list = []
last_good_items = []
picture = []
bypass = True

def bot():
    while True:
        itemz, decrease_margin, exp_pages, webhook_link = get_settings()

        # <----- selenium configuration ----->
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        driver1 = webdriver.Firefox(options=options)
        # <----- counting vars ----->
        count = 1
        item_count = 0

        # creation of list
        items_list = []
        final_list = []
        good_items = []


        # find items
        for _ in range(int(exp_pages)):
            # progressbar
            print("10% - Pages exploration...")
            try:
                items = []
                driver1.get(link_builder(count))
                # Wait for the page to fully load and the element to be visible
                WebDriverWait(driver1, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a.new-item-box__overlay.new-item-box__overlay--clickable")))
                count = count + 1
                items = items + driver1.find_elements(By.CSS_SELECTOR, "a.new-item-box__overlay.new-item-box__overlay--clickable")

                for item in items:
                    it1 = item.get_attribute('href')
                    it2 = item.get_attribute('title')
                    it = it1 + ", " + it2
                    items_list.append(it)

            except Exception as e:
                e

        print("20% - Item classification..")

        # extract scraped elements 

        for i in range(0, len(items_list), 1):
            item_count = item_count + 1
            final_list.append(items_list[i:i+1])

        # doublets deleter
        final_list = remove_duplicate(final_list)
        
        # find image and class the products

        print("50% Exploration of items... ()")

        for i in range(0,len(final_list)-1,1):
            text_to_regex = final_list[i]
            prezzo=re.findall(r'\b\d{1,4}(?:,\d{2})\b', text_to_regex[0])[0]
            href = re.findall(r'https:\/\/www\.vinted\.it\/items\/\d+-[a-zA-Z0-9-]+(?:\?.*)?', text_to_regex[0])[0].split(",")[0]
            titolo = text_to_regex[0].split(",")[1]
            prezzo = str(prezzo)+"€"
            if ([titolo, prezzo, href] not in last_good_items):
                good_items.append([titolo, prezzo, href])
                last_good_items.append([titolo, prezzo, href])
                price_list.append(prezzo)

        # detect no product found
        if good_items == []:
            system('cls' if os.name == 'nt' else 'clear')
            print("items not found :/")
        else:
            pass

        print("80% - Sending information to webhook..")  


        def webhook_start():
            webhook_sender(item, webhook_link)

        if(bypass == False):
            for item in good_items:
                print("80% - Sending information to webhook.." + str(good_items.index(item)) + "/" + str(len(good_items)) + " items sent")
                webhook_start()
        else:
            bypass = False
        
        print("100% - Operation completed !.. - Waiting for next cycle (5min)")
        driver1.close()
        try:
            remove("geckodriver.log")
        except:
            pass
        sleep(300)

if __name__ == "__main__":
    bot()