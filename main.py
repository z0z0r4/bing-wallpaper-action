import httpx
import asyncio
import datetime
import os
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


REGION_LIST = ["en-US", "zh-CN", "ja-JP", "de-DE", "en-GB", "es-ES",
           "pt-BR", "en-AU", "en-CA", "fr-FR", "en-IN"]

BING_ROOT = "https://www.bing.com"
CACHE_PATH = "cache"
INFO_PATH = "info"

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

# DRIVER = init_driver()

if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)

if not os.path.exists(INFO_PATH):
    os.makedirs(INFO_PATH)

async def get(url: str, *args, **kwargs) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.get(url, timeout=60, *args, **kwargs)

async def get_region_info(region: str):
    jsonurl = f"https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt={region}"
    img_info = (await get(jsonurl)).json()["images"][0]
    # img_info["desc"] = get_description_from_browser(region=region, date=img_info["startdate"]) SB Bing
    return img_info

async def cache_img(info: dict, region: str) -> None:
    save_path = os.path.join(CACHE_PATH, f'{info["hsh"]}.jpg')
    if os.path.exists(save_path):
        print(
            f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {region} {info["title"]} {info["hsh"]} 已存在')
    else:
        image_url = BING_ROOT + info["urlbase"] + "_UHD.jpg"
        with open(save_path, "wb") as file:
            file.write((await get(image_url)).content)
        print(
            f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {region} {info["title"]} {info["hsh"]} 缓存完成')

async def cache_info(info: dict, region: str) -> None:
    region_info_path = os.path.join(INFO_PATH, f"{region}.json")
    if os.path.exists(region_info_path):
        # 读取缓存信息
        with open(region_info_path, encoding="UTF-8") as info_file:
            wallpaper_info_json = json.load(info_file)
            wallpaper_info_json[info["hsh"]] = info
        # 写入缓存信息
        with open(region_info_path, "w", encoding="UTF-8") as info_file:
            json.dump(wallpaper_info_json, info_file, ensure_ascii=False, indent=4)
    else:
        # init
        with open(region_info_path, "w", encoding="UTF-8") as info_file:
            json.dump({info["hsh"]: info}, info_file, ensure_ascii=False, indent=4)

def get_description_from_browser(region: str, date: str):
    print(f"===={region}===={date}====")
    url = f'https://www.bing.com/search?q=0&form=hpcapt&filters=HpDate:"{date}"&mkt={region}'
    DRIVER.get(url)
    DRIVER.implicitly_wait(1)
    print(DRIVER.page_source)
    try:
        co = DRIVER.find_element(By.ID, 'bnp_btn_accept').click()
    except Exception as e:
        pass
    try:
        co = DRIVER.find_element(By.XPATH, '//*[@id="bs-readmore"]').click()
    except Exception as e:
        pass
    # WebDriverWait(DRIVER, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="bs-readmore"]'))).click()
    # WebDriverWait(DRIVER, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ency_desc_full"]')))
    element_xpath = '//*[@id="ency_desc_full"]'
    e = DRIVER.find_element(By.XPATH, element_xpath)
    text = e.text
    return e.text

async def process_region(region: str):
    img_info = await get_region_info(region)
    await cache_img(img_info, region)
    await cache_info(img_info, region)

async def main():
    tasks = []
    for region in REGION_LIST:
        tasks.append(asyncio.create_task(process_region(region)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
