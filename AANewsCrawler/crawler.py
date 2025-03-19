import json
import os
import keyboard as kb
import requests as r
from pyquery import PyQuery as pq

from data import News

class Crawler:
    
    def __init__(self) -> None:
        self.data_file = './news.json'
        
        self.tr_url = 'https://www.aa.com.tr/tr'
        self.base_url = 'https://www.aa.com.tr/tr/gundem/abcdefg/'
        self.imagedefs_file = "./images/image_definitions.csv"
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/111.0.0.0 Safari/537.36'
        }
        self.home_url = 'https://www.aa.com.tr/'
        self.load_news()

    
    def get_news(self, begin, end):
        if(self.next_news>begin):
            current = self.next_news
        else:
            current = begin
        step = 1

        while current<end:
            if kb.is_pressed('escape'):
                break
            
            try:
                current_link = self.base_url+str(current)
                resp = r.get(url = current_link, timeout=5, headers= self.headers)
                
                resp_url = resp.url
                if resp_url != current_link and len(resp_url) > len(current_link):
                    
                    temp = News(current)
                    source = pq(resp.content)
                    image_link = source.find('img.detay-buyukFoto').attr('src')
                    image_def = source.find('img.detay-buyukFoto').attr('alt')
                    self.save_image(image_link, image_def, current)
                    
                    temp.setLink(resp_url) 
                    temp.Title = source.find('h1').text()
                    temp.Summary = source.find('h4').text()
                    spans = source.find('detay-spot-category span')
                    print(spans.text)
                    temp.Date = source.find('span.tarih').text().split(' ')[0] 
                    temp.Body = source.find('div.detay-icerik p').text()
                    news_parts = resp_url.replace(self.home_url, '').split('/')
                    temp.Language = news_parts[0]
                    temp.Category = news_parts[1]
 
                    current_news = temp.get_JSON()  
                    self.news_list.append(current_news)
                    print(str(temp.getID()).rjust(7)+" - "+temp.getTitle())

                current = current + step

            except r.exceptions.ConnectTimeout:
                print(str(current).rjust(7)+". ------Connecting timeout for \n"+current_link+"\n-------")
            except r.exceptions.InvalidURL:
                print(str(current).rjust(7)+". ------Invalid url error for \n"+current_link+"\n-------")
            except r.exceptions.ConnectionError:  
                print(str(current).rjust(7)+". ------Connection error for \n"+current_link+"\n-------")
            except r.exceptions.Timeout:
                print(str(current).rjust(7)+". ------Time out for \n"+current_link+"\n-------")


    def save_news(self):
        with open(self.data_file, "w") as data:
            json.dump(self.news_list, data)


    def load_news(self):
        if os.path.isfile(self.data_file):
            with open(self.data_file, "r") as data:
                self.news_list = json.load(data)
                data.close()
                last_news = self.news_list[len(self.news_list)-1]
                self.next_news = int(last_news["ID"])+1

        else:
            self.news_list = list()
            self.next_news = -1

    
    def save_image(self, image_link, image_def, ID):
        res_image = r.get(image_link, headers = self.headers)
        folder_name = './images/'+ str(int(ID/100)*100)+"/"
        
        if not os.path.exists(folder_name):
           os.mkdir(folder_name) 

        image_name = folder_name+str(ID)+".jpg"
        with open(image_name, "wb") as f:
            f.write(res_image.content)
            f.close()
        with open(self.imagedefs_file, "a", encoding="utf-8") as im:
            im.write(str(ID)+"\t"+image_def+"\n")
            im.close()