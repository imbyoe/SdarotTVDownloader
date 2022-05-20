from msilib.schema import Error
import requests
import os
import threading
from selenium import webdriver
import requests
import time 

print("please provide a series id: ")
id = input("> ")
print("please provide the season to start with: ")
seasons = int(input("> "))
print("please provide the season to stop: ")
seasons_end = int(input("> "))
def download_thread(link):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('log-level=3')
        driver = webdriver.Chrome(options=options)
        season= link.split("/season/")[1].split("/episode/")[0]
        num = link.split("/episode/")[1]
        driver.get(link)
        series_name = driver.find_element_by_class_name("ltr").get_attribute('innerText')
        series_name = series_name.replace(":","")
        os.makedirs(f'{series_name}/Season {season}', exist_ok=True)
        time.sleep(13)
        if driver.current_url.replace("www.","").replace("https://","").replace("http://","").replace("/","") == "sdarot.tv":
            open("skipped_urls.txt","a").write(link+"\n")
            return
        while True:
            time.sleep(6)
            try:
                if driver.find_element_by_id("waitTime").get_attribute("class") == "hidden":
                    if driver.find_element_by_id("afterLoad").get_attribute("class") == "hidden":
                        driver.refresh();
                        time.sleep(12)
                    else:
                        driver.find_element_by_id("proceed").click()
                        break           
            except:
                continue
        r = requests.get(driver.find_element("id","videojs_html5_api").get_attribute("src"), stream = True,headers={
            "cookie": "Sdarot="+driver.get_cookies()[3].get("value")
        }) 

        with open(f"{series_name}/Season {season}/{series_name} - s{season}e{num}.mp4", 'wb') as f: 
            for chunk in r.iter_content(chunk_size = 1024*1024): 
                if chunk: 
                    f.write(chunk)
    except Exception as e:
        print(e)
        download_thread(link)
bursts = 4
for i in range(seasons,seasons_end+1):
    options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://sdarot.tv/watch/{id}/season/{i}")
    episodes_ = driver.find_element_by_id("episode").find_elements_by_class_name("text-center")
    episodes = []
    for episode in episodes_:
        episodes.append(episode.get_attribute("href"))
    driver.close()
    threads = []
    for ii in episodes:
        if len(threads) >= bursts:
            threads[0].join()
            threads.remove(threads[0])
        thread = threading.Thread(target=download_thread, args=(ii,))
        threads.append(thread)
        thread.start()
        time.sleep(5)
    time.sleep(20)
