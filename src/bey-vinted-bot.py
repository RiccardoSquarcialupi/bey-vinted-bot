from selenium import webdriver
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from os import getcwd, remove
from discord_webhook import DiscordWebhook, DiscordEmbed
from time import sleep
from json import load, dump
from colorama import Fore
from requests import get
from pyshorteners import Shortener
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

# ----- colorama settings -----
c = Fore.LIGHTCYAN_EX
w = Fore.LIGHTWHITE_EX

# ----- banner -----
banner = f"""                 )                  (         )                  (                       )            
   (           ( /(                  )\ )   ( /(    *   )         )\ )            (    ( /(     *   )  
 ( )\   (      )\())        (   (   (()/(   )\()) ` )  /(   (    (()/(          ( )\   )\())  ` )  /(  
 )((_)  )\    ((_)\   ___   )\  )\   /(_)) ((_)\   ( )(_))  )\    /(_))   ___   )((_) ((_)\    ( )(_)) 
((_)_  ((_)  __ ((_) |___| ((_)((_) (_))    _((_) (_(_())  ((_)  (_))_   |___| ((_)_    ((_)  (_(_())  
 | _ ) | __| \ \ / /       \ \ / /  |_ _|  | \| | |_   _|  | __|  |   \         | _ )  / _ \  |_   _|  
 | _ \ | _|   \ V /         \ V /    | |   | .` |   | |    | _|   | |) |        | _ \ | (_) |   | |    
 |___/ |___|   |_|           \_/    |___|  |_|\_|   |_|    |___|  |___/         |___/  \___/    |_|                                                                                                   
"""


# <----- json file reader ----->
def read_json(file_path: str) -> dict:
    with open(file_path, 'r') as json_file:
        data = load(json_file)
    return data

# <----- json file writer ----->
def write_json(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as json_file:
        dump(data, json_file)
        
# <----- remove duplicate ----->
def remove_duplicate(list):
    return [x for i, x in enumerate(list) if x not in list[:i]]

# <----- get settings ----->
def get_settings():
    json_data = read_json(f"{getcwd()}"+os.sep+"assets"+os.sep+"settings.json")
    return json_data["Item"], json_data["Margin"], json_data["Explored_pages"], json_data["Webhook"]

def info_getter(link):
    chrome_options = webdriver.ChromeOptions()    
    # Add your options as needed    
    options = [
    # Define window size here
    "--window-size=1200,1200",
        "--ignore-certificate-errors"
    
        "--headless",
        #"--disable-gpu",
        #"--window-size=1920,1200",
        #"--ignore-certificate-errors",
        #"--disable-extensions",
        #"--no-sandbox",
        #"--disable-dev-shm-usage",
        #'--remote-debugging-port=9222'
    ]

    for option in options:
        chrome_options.add_argument(option)

        
    driver = webdriver.Chrome(options = chrome_options)
    driver.get(link)
    try:
        wait = WebDriverWait(driver, 10)
        imgParent = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='item-photo-1--img']")))
        img = imgParent.get_attribute('src')
        desc = driver.find_element(By.CSS_SELECTOR, "span.web_ui__Text__text.web_ui__Text__body.web_ui__Text__left.web_ui__Text__format").text
    except Exception as e:
        driver.close()
        return img, "No description found..." #cdc
    driver.close()
    return img, desc
# <----- webhook sender ----->
def webhook_sender(item, webhook_link):
    try:
        webhook = DiscordWebhook(
                url=webhook_link,
                username="Vinted Bot",)
        embed = DiscordEmbed(title=item[0], color='FF1F1F')
        
        image, desc = info_getter(item[2])
        desc1 = desc.lower().split(" ")
        if 'burst' in desc1 or 'masters' in desc1 or 'fusion' in desc1:
            print("is a burst/metal item, fuck off we want only plastic gen broski")
        else:
            word_list = read_json(f"{getcwd()}"+os.sep+"assets"+os.sep+"plastic.json")
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
                print("No valid words found in the description, skipping...")
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
    link = "https://www.vinted.it/catalog?search_text=beyblade&brand_ids[]=270688&brand_ids[]=114196&brand_ids[]=330038&brand_ids[]=65554&brand_ids[]=165516&brand_ids[]=281034&order=newest_first&page=" + str(count) + "'"
    return link
    
    
# <----- progress bar ----->
def progressbar(banner, w, bar):
    print(f"\n{banner}\n {w}{bar}")

def shortlink(link):
    s = Shortener()
    return s.tinyurl.short(link)
    
def bot(items_list, final_list, price_list, last_good_items, bypass):
    h = 0
    while h < 2:
        h=h+1
        import sys
        sys.stdout.flush()
        _,_, exp_pages, webhook_link = get_settings()

        # <----- selenium configuration ----->
        chrome_options = webdriver.ChromeOptions()    
        # Add your options as needed    
        options = [
        # Define window size here
        "--window-size=1200,1200",
            "--ignore-certificate-errors"
        
            "--headless",
            #"--disable-gpu",
            #"--window-size=1920,1200",
            #"--ignore-certificate-errors",
            #"--disable-extensions",
            #"--no-sandbox",
            #"--disable-dev-shm-usage",
            #'--remote-debugging-port=9222'
        ]

        for option in options:
            chrome_options.add_argument(option)

            
        driver1 = webdriver.Chrome(options = chrome_options)
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
        # Load last_good_items from history.json
        last_good_items = read_json(os.path.join(getcwd(), "assets", "history.json"))

        last_good_items_tuples = [(item['titolo'], item['prezzo'], item['href']) for item in last_good_items.values()]

        for i in range(0,len(final_list)-1,1):
            text_to_regex = final_list[i]
            prezzo=re.findall(r'\b\d{1,4}(?:,\d{2})\b', text_to_regex[0])[0]
            href = re.findall(r'https:\/\/www\.vinted\.it\/items\/\d+-[a-zA-Z0-9-]+(?:\?.*)?', text_to_regex[0])[0].split(",")[0]
            titolo = text_to_regex[0].split(",")[1]
            prezzo = str(prezzo)+"€"
            # Check if the tuple is not in last_good_items_tuples
            if (titolo, prezzo, href) not in last_good_items_tuples:
                good_items.append([titolo, prezzo, href])
                last_good_items[len(last_good_items)] = {'titolo': titolo, 'prezzo': prezzo, 'href': href}
                price_list.append(prezzo)

        # detect no product found
        if good_items == []:
            print("items not found :/")
        else:
            pass

        print("80% - Sending information to webhook..")  


        def webhook_start():
            webhook_sender(item, webhook_link)

        write_json(f"{getcwd()}"+os.sep+"assets"+os.sep+"history.json", last_good_items)

        if(bypass == False):
            for item in good_items:
                print("80% - Sending information to webhook.." + str(good_items.index(item)) + "/" + str(len(good_items)) + " items sent")
                webhook_start()
        else:
            bypass = False
        
        print("100% - Operation completed !.. - Waiting for next cycle (30sec)")
        driver1.close()
        try:
            remove("geckodriver.log")
        except:
            pass

if __name__ == "__main__":
    # <----- bot ----->
    import os
    #ubuntu latest version
    
    if os.name == 'nt':
        os.environ['TERM'] = 'xterm'
    
    print(banner) 
    # bot settings
    items_list = []
    final_list = []
    price_list = []
    last_good_items = []
    bypass = False
    bot(items_list, final_list, price_list, last_good_items, bypass)
