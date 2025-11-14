# -*- coding: utf-8 -*-
"""
Created on 2025-10-30 10:04:34
---------
@summary:
---------
@author: lucas
"""
import json
import random
import time

import feapder
from feapder import Response, Request
from feapder.db.redisdb import RedisDB
from feapder.utils.log import log
from playwright.sync_api import Page

from items.spider_web_img_url_item import SpiderWebImgUrlItem

account = "13291413488"
password = "wow-trend123"

# women men kids 的服装和鞋子
urls = [
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}",
]
urls_mapping = {
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}": "women clothes",
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}": "women shoes",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}": "men clothes",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}": "men shoes",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}": "kids clothes",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}": "kids shoes",
}

user_table = "spider:aigc:image:wow"
class AigcWowSpider(feapder.AirSpider):
    def __init__(self, thread_count=None, url_index=0):
        super().__init__(thread_count)
        self._redisdb = RedisDB()
        self.url_index = int(url_index)

    def start_requests(self):
        yield feapder.Request(
            url=urls[self.url_index].format(pageNum=1),
            pageNum=1,
            total_page=236,
            current_count=0,
            render=True,
            orignal_url=urls[self.url_index],
        )

    def download_midware(self, request: Request):
        cookies = self._redisdb.hget(user_table, "cookies", False)
        if isinstance(cookies, str):
            cookies = eval(cookies)
        request.cookies = cookies
        return request


    def parse(self, request, response):
        pageNum = request.pageNum
        total_page = request.total_page
        current_count = request.current_count
        if not response.ok:
            raise Exception(f"{request.url} 访问失败")

        css_selectors = self.build_css()
        page: Page = response.driver.page

        # 登陆
        login_btn = self.retry_locate(page, css_selectors["login"])
        if login_btn:
            login_btn = self.retry_locate(page, css_selectors["login"])
            login_btn.first.click()
            username = self.retry_locate(page, css_selectors["username"])
            username.first.fill(account)
            passwd = self.retry_locate(page, css_selectors["password"])
            passwd.first.fill(password)
            submit_btn = self.retry_locate(page, css_selectors["submit"])
            submit_btn.first.click()
            time.sleep(2)
            cookies = page.context.cookies()
            self._redisdb.hset(user_table, "cookies", cookies)


        for i in range(random.randint(10, 15)):
            page.keyboard.press("PageDown")
            time.sleep(1)

        first_img = self.retry_locate(page, css_selectors["all_images"])
        first_img.first.click()

        next_image = self.retry_locate(page, css_selectors["next_image"])
        next_btn = next_image.last

        response = Response.from_text(page.content())
        soup = response.bs4()
        imgs, _ = self.retry_find(soup, css_selectors["all_images"])
        current_count += len(imgs)
        log.info(f"当前爬取页码 {pageNum}, 累计抓取图片数 {current_count}")

        start_time = time.time()
        # 开始爬取图片链接
        old_url = ""
        while True:
            next_image = self.retry_locate(page, css_selectors["next_image"])
            if not next_image:
                break
            next_btn = next_image.last
            ist= self.retry_locate(page, css_selectors["image_list"], timeout=1000)
            if ist:
                if len(ist.all()) > 1:
                    for item in ist.all():
                        item.click()
                        old_url,url = self.parse_page(old_url, page, css_selectors)
                    next_image = self.retry_locate(page, css_selectors["next_image"])
                    if not next_image:
                        break
                    next_btn = next_image.last
                else:
                    old_url,url = self.parse_page(old_url, page, css_selectors)
            else:
                old_url,url = self.parse_page(old_url, page, css_selectors)

            yield SpiderWebImgUrlItem(
                website="wow",
                # title=title,
                tags=urls_mapping[request.orignal_url],
                url=url,
            )
            try:
                next_btn.click(timeout=1000)
                time.sleep(0.6)
            except:
                continue

        log.info(f"当前爬取页码 {pageNum}, 耗时 {time.time()-start_time}s")

        pageNum += 1
        request.url = request.orignal_url.format(pageNum=pageNum)
        request.pageNum = pageNum
        request.total_page = total_page
        request.current_count = current_count
        yield request

    def parse_page(self, old_url, page, css_selectors):
        while True:
            time.sleep(0.5)
            response = Response.from_text(page.content())
            soup = response.bs4()
            image, _ = self.retry_find(soup, css_selectors["big_image"])
            if image:
                url = image[0].get("src")
                if old_url != url:
                    old_url = url
                else:
                    continue
            else:
                continue
            break
        return old_url, url

    @staticmethod
    def build_css():
        css = {
            "login": [
                """div[class*="login"] span[title="登录/注册"]""",
            ],
            "username": [
                """input[name="username"]""",
            ],
            "password": [
                """input[name="password"]""",
            ],
            "submit": [
                """input[type="submit"][class*="sumbit"]"""
            ],
            "all_images": [
                """div[class*="carousel-container"]"""
            ],
            "big_image": [
                """div.zoom-img-box > img"""
            ],
            "image_list": [
                """div[class*="drawingItem"][id*="ass"]"""
            ],
            "next_image": [
                """div[class*="nextPage"]"""
            ],
        }
        return css

    @staticmethod
    def retry_find(soup, selectors):
        for selector in selectors:
            results = soup.select(selector)
            if results:
                return results, selector
        return [], ""

    @staticmethod
    def retry_locate(page, selectors, state="attached", timeout=5000):
        for selector in selectors:
            item = page.locator(selector)
            try:
                item.first.wait_for(state=state, timeout=timeout)
            except:
                # import traceback
                # traceback.print_exc()
                continue
            return item
        return None


if __name__ == "__main__":
    url_index = input("-->")
    AigcWowSpider(url_index=url_index).start()
