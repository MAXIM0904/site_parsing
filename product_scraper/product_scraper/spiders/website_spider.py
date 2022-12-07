import scrapy
from selenium import webdriver
from scrapy.selector import Selector
import time
import pandas as pd


class WebsiteSpider(scrapy.Spider):
    name = "website"
    start_urls = "https://www.ozon.ru/category/smartfony-15502/?sorting=rating"

    @staticmethod
    def __webdriver_spider(url, min_scroll, max_scroll):
        driver = webdriver.Chrome("product_scraper/chromedriver.exe")
        driver.get(url)
        time.sleep(3)
        driver.execute_script(f"window.scrollTo({min_scroll},{max_scroll});")
        time.sleep(3)
        sel = Selector(text=driver.page_source)
        driver.close()
        return sel

    def start_requests(self):
        page = 1
        url = self.start_urls
        count_phone = 0
        list_system = []

        while count_phone <= 100:
            sel = self.__webdriver_spider(url=url, min_scroll=5, max_scroll=10000)
            phone_links = sel.xpath(
                '//div[@class="wk6 w6k"]/div[@class="kw7"]/a[starts-with(@href, "/product")]/@href'
            ).getall()
            url = f"https://www.ozon.ru/category/smartfony-15502/?page={page}" \
                  f"&sorting=rating&tf_state=aHpE44-GY6MHQHBAJVMdzNWG_RaXE9MJgb-Axnrw45NpBkd8"
            page += 1

            for link in phone_links:
                url_link = f"https://www.ozon.ru{link}"
                sel = self.__webdriver_spider(url=url_link, min_scroll=5, max_scroll=6000)
                operating_system = sel.xpath(
                    '//dl[@class="m6p"]/dd[contains(text(),"iOS ") or contains(text(),"Android ")]/text()'
                ).getall()

                if not operating_system:
                    operating_system = sel.xpath(
                        '//dd[@class="pm5"]/a[contains(text(),"iOS ") or contains(text(),"Android ")]/text()'
                    ).getall()

                if operating_system:
                    count_phone += 1
                    list_system.append(operating_system)
                    if count_phone >= 100:
                        break

            if count_phone >= 100:
                break

        df = pd.Series(system[0] for system in list_system)
        answer = df.value_counts(sort=True).to_dict()
        for key, value in answer.items():
            with open('system_versions.txt', 'a', encoding='utf-8') as f:
                f.write(f"{key}: {value}\n")
