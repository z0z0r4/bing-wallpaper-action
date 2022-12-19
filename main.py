import requests
import datetime
import os
import json

# mktlist = ["en-US", "zh-CN", "ja-JP", "de-DE"]
bing_domain = "https://cn.bing.com"

if not os.path.exists("wallpaper_cache"):
    os.makedirs("wallpaper_cache")

mkt = "zh-CN"
jsonurl = f"https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt={mkt}"
img_json = requests.get(jsonurl).json()["images"][0]
save_path = os.path.join("wallpaper_cache", f'{img_json["title"]}_{img_json["enddate"]}_{mkt}_{img_json["hsh"][:6]}.png')
if os.path.exists(save_path):
    print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {img_json["title"]} {img_json["enddate"]} {mkt} 已存在')
else:
    image_url = bing_domain + img_json["url"]
    with open(save_path, "wb") as file:
        file.write(requests.get(image_url).content)
    print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {img_json["title"]} {img_json["enddate"]} {mkt} 缓存完成')

if os.path.exists(os.path.join("wallpaper_cache", "wallpaper_info.json")):
    with open(os.path.join("wallpaper_cache", "wallpaper_info.json"), encoding="UTF-8") as info_file:
        wallpaper_info_json = json.load(info_file)
        wallpaper_info_json["wallpaper_info"][img_json["enddate"]] = img_json
    with open(os.path.join("wallpaper_cache", "wallpaper_info.json"), "w", encoding="UTF-8") as info_file:
        json.dump(wallpaper_info_json, info_file, ensure_ascii=False)
else:
    with open(os.path.join("wallpaper_cache", "wallpaper_info.json"), "w", encoding="UTF-8") as info_file:
        json.dump({"wallpaper_info": {img_json["enddate"]: img_json}}, info_file, ensure_ascii=False)