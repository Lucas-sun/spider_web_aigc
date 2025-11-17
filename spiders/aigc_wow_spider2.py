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
import re
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
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A937%2C%22name%22%3A%22%E9%85%8D%E9%A5%B0%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A935%2C%22name%22%3A%22%E5%8C%85%E8%A2%8B%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A937%2C%22name%22%3A%22%E9%85%8D%E9%A5%B0%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A935%2C%22name%22%3A%22%E5%8C%85%E8%A2%8B%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A937%2C%22name%22%3A%22%E9%85%8D%E9%A5%B0%22%7D%5D&page={pageNum}",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A935%2C%22name%22%3A%22%E5%8C%85%E8%A2%8B%22%7D%5D&page={pageNum}",
]
urls_mapping = {
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}": "women clothes",
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}": "women shoes",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}": "men clothes",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}": "men shoes",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A433782%2C%22name%22%3A%22%E6%9C%8D%E8%A3%85%22%7D%5D&page={pageNum}": "kids clothes",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A933%2C%22name%22%3A%22%E9%9E%8B%E5%B1%A5%22%7D%5D&page={pageNum}": "kids shoes",
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A937%2C%22name%22%3A%22%E9%85%8D%E9%A5%B0%22%7D%5D&page={pageNum}": "women accessories",
    "https://www.wow-trend.com/searchpage/?gender_id=72105&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A935%2C%22name%22%3A%22%E5%8C%85%E8%A2%8B%22%7D%5D&page={pageNum}": "women bags",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A937%2C%22name%22%3A%22%E9%85%8D%E9%A5%B0%22%7D%5D&page={pageNum}": "men accessories",
    "https://www.wow-trend.com/searchpage/?gender_id=72103&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A935%2C%22name%22%3A%22%E5%8C%85%E8%A2%8B%22%7D%5D&page={pageNum}": "men bags",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A937%2C%22name%22%3A%22%E9%85%8D%E9%A5%B0%22%7D%5D&page={pageNum}": "kids accessories",
    "https://www.wow-trend.com/searchpage/?gender_id=72107&keywords=&type=picture&filter=%5B%7B%22group_id%22%3A116%2C%22id%22%3A935%2C%22name%22%3A%22%E5%8C%85%E8%A2%8B%22%7D%5D&page={pageNum}": "kids bags",
}

user_table = "spider:aigc:image:wow"


class AigcWowSpider(feapder.AirSpider):
    def __init__(self, thread_count=None, url_index=0):
        super().__init__(thread_count)
        self._redisdb = RedisDB()
        self.url_index = int(url_index)

    def start_requests(self):
        # 0 10384
        # 2 9353
        # 3 1
        # 4 2078
        start_page = 1
        yield feapder.Request(
            url=urls[self.url_index].format(pageNum=start_page),
            pageNum=start_page,
            total_page=100+start_page,
            current_count=0,
            render=True,
            orignal_url=urls[self.url_index],
            updated=False,
        )

    def download_midware(self, request: Request):
        cookies = self._redisdb.hget(user_table, "cookies", False)
        if isinstance(cookies, str):
            cookies = eval(cookies)
        request.cookies = cookies
        return request

    def parse(self, request, response):
        start_time = time.time()
        pageNum = request.pageNum
        total_page = request.total_page
        current_count = request.current_count
        updated = request.updated
        tag = urls_mapping[request.orignal_url]
        data = []
        if not response.ok:
            raise Exception(f"{request.url} 访问失败")

        css_selectors = self.build_css()
        page: Page = response.driver.page

        def on_response(response):
            rex = r"api/trend/find/search-index"
            if re.search(rex, response.url, re.IGNORECASE):
                try:
                    rdata = response.json()
                    ddata = self.parse_response(rdata, tag)
                    data.extend(ddata)
                except:
                    txt = response.text
                    log.error(f"页面请求code {response.status}, 页面地址 {response.url}, {txt[:500]}")

        page.on("response", on_response)

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

        for i in range(random.randint(20, 30)):
            page.keyboard.press("PageDown")
            time.sleep(0.5)

        page.remove_listener("response", on_response)

        for item in data:
            yield SpiderWebImgUrlItem(**item, website="wow")

        response = Response.from_text(page.content())
        soup = response.bs4()
        if not updated:
            npages, _ = self.retry_find(soup, css_selectors["total_page"])
            if npages:
                total_page = int(npages[-1].get("title"))
                updated = True
        current_count += len(data)
        log.info(f"当前爬取页码 {pageNum}, 累计抓取图片数 {current_count}")
        log.info(f"当前爬取页码 {pageNum}, 耗时 {time.time() - start_time}s")


        if pageNum <= total_page:
            imgs, _ = self.retry_find(soup, css_selectors["total_page"])
            pageNum += 1
            request.url = request.orignal_url.format(pageNum=pageNum)
            request.pageNum = pageNum
            request.total_page = total_page
            request.current_count = current_count
            request.updated = updated
            yield request

    def parse_response(self, response_data: dict, first_tag: str) -> list[dict]:
        """
        解析API请求返回数据
        :param response_data:
        :return:
        """
        data = []
        rdata = response_data.get("data", {})
        rlist = rdata.get("list", [])
        for ritem in rlist:
            url = ritem.get("hd_picture", "")
            title = ritem.get("title", "")
            tags = [first_tag] + [t.get("tag_name", "") for t in ritem.get("attrs", [])]
            if len(tags) > 1:
                tags = ",".join(tags)
            else:
                tags = f"{tags[0]},"
            data.append({
                "url": url,
                "title": title,
                "tags": tags,
            })
        return data

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
            "total_page": [
                """li[class*="ant-pagination-item"]"""
            ]
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
