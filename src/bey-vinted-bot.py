import os
import re
import sys
import json
from time import sleep
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from discord_webhook import DiscordWebhook, DiscordEmbed
from pyshorteners import Shortener
from pyvirtualdisplay import Display
from colorama import Fore
import chromedriver_autoinstaller

# Constants
DISPLAY_SIZE = (800, 800)
WEBHOOK_USERNAME = "Vinted Bot"
SEARCH_URL_TEMPLATE = "https://www.vinted.it/catalog?search_text=beyblade&brand_ids[]=270688&brand_ids[]=114196&brand_ids[]=330038&brand_ids[]=65554&brand_ids[]=165516&brand_ids[]=281034&order=newest_first&page={}"
ASSETS_PATH = os.path.join(os.getcwd(), "assets")
BANNER = f"""..."""  # Shortened banner for clarity

# Setup virtual display for headless environments
display = Display(visible=0, size=DISPLAY_SIZE)
display.start()

# Auto-install ChromeDriver
chromedriver_autoinstaller.install()

# Colorama settings
c = Fore.LIGHTCYAN_EX
w = Fore.LIGHTWHITE_EX

def load_json(file_path):
    """Reads JSON data from the specified file path."""
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    """Writes JSON data to the specified file path."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def remove_duplicates(lst):
    """Removes duplicates from a list."""
    return list(dict.fromkeys(lst))

def get_settings():
    """Loads settings from the settings.json file."""
    settings = load_json(os.path.join(ASSETS_PATH, "settings.json"))
    return settings["Item"], settings["Margin"], settings["Explored_pages"], settings["Webhook"]

def setup_webdriver():
    """Sets up Chrome WebDriver with desired options."""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1200,1200")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)

def get_item_info(driver, url):
    """Fetches item image and description from the given URL."""
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 10)
        img_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='item-photo-1--img']")))
        image_url = img_element.get_attribute('src')
        description = driver.find_element(By.CSS_SELECTOR, "span.web_ui__Text__text").text
        return image_url, description
    except Exception:
        return None, "No description found"

def send_webhook(item, webhook_url):
    """Sends item information to a Discord webhook."""
    image, description = get_item_info(setup_webdriver(), item[2])
    if not image:
        return

    description_words = description.lower().split(" ")
    if any(word in description_words for word in ['burst', 'masters', 'fusion']):
        print("Skipping non-plastic generation item...")
        return

    valid_words = load_json(os.path.join(ASSETS_PATH, "plastic.json"))["beyblade_words"]
    matched_words = [word for word in valid_words if word in description_words]

    if matched_words:
        webhook = DiscordWebhook(url=webhook_url, username=WEBHOOK_USERNAME)
        embed = DiscordEmbed(title=item[0], color='FF1F1F')
        embed.set_image(image)
        embed.add_embed_field(name='Price :dollar:', value=f"{item[1].replace(' prezzo:', '')}€")
        embed.add_embed_field(name='Product Link :link:', value=shorten_url(item[2]), inline=True)
        embed.add_embed_field(name='Description :label:', value=f"{matched_words[0]} - {description}", inline=True)
        embed.set_author(name='RiccardoSquarcialupi', icon_url='https://avatars.githubusercontent.com/u/44367261?v=4')
        embed.set_footer(text='Let it RIP!!!')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
    else:
        print("No valid words found, skipping item...")

def shorten_url(url):
    """Shortens a URL using TinyURL."""
    return Shortener().tinyurl.short(url)

def link_builder(page_count):
    """Builds a Vinted search URL based on the page number."""
    return SEARCH_URL_TEMPLATE.format(page_count)

def explore_items(driver, pages_to_explore):
    """Extracts item links from the Vinted search results."""
    item_links = []
    for page in range(1, pages_to_explore + 1):
        driver.get(link_builder(page))
        try:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a.new-item-box__overlay--clickable")))
            items = driver.find_elements(By.CSS_SELECTOR, "a.new-item-box__overlay--clickable")
            for item in items:
                href = item.get_attribute('href')
                title = item.get_attribute('title')
                item_links.append(f"{href}, {title}")
        except Exception:
            pass
    return remove_duplicates(item_links)

def run_bot():
    """Main bot logic."""
    print(BANNER)
    items_list, final_list, price_list, last_good_items, bypass = [], [], [], [], False

    _, _, explored_pages, webhook_url = get_settings()
    driver = setup_webdriver()

    items_list = explore_items(driver, explored_pages)
    driver.quit()

    for item in items_list:
        price = re.findall(r'\b\d{1,4}(?:,\d{2})\b', item)[0]
        href = re.findall(r'https:\/\/www\.vinted\.it\/items\/\d+-[a-zA-Z0-9-]+', item)[0]
        title = item.split(",")[1].strip()
        price = f"{price}€"
        final_list.append([title, price, href])

    if final_list:
        last_good_items_data = load_json(os.path.join(ASSETS_PATH, "history.json"))
        for item in final_list:
            send_webhook(item, webhook_url)
        save_json(os.path.join(ASSETS_PATH, "history.json"), last_good_items_data)
        print("Webhook sent successfully.")
    else:
        print("No new items found.")

if __name__ == "__main__":
    if os.name == 'nt':
        os.environ['TERM'] = 'xterm'
    run_bot()
