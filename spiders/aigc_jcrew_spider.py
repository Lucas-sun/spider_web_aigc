# -*- coding: utf-8 -*-
"""
Created on 2025-10-29 09:27:38
---------
@summary:
---------
@author: lucas
"""
from copy import deepcopy

import feapder
from feapder.utils.log import log

from items.spider_web_img_url_item import SpiderWebImgUrlItem


class AigcJcrewSpider(feapder.AirSpider):
    def start_requests(self):
        urls = [
            "https://www.jcrew.com/plp/mens/categories/clothing",
            "https://www.jcrew.com/plp/womens/categories/clothing",
        ]
        for url in urls:
            yield feapder.Request(
                url=url,
                method="GET",
                params={"Nrpp": 120, "Nsrt": "Newest"},
                render=True,
                finished=False,
            )

    def parse(self, request, response):
        pageNum = request.get_params().get("Npge", 1)
        finished = request.finished
        if not response.ok:
            raise Exception(f"{request.url}爬取失败")

        css = self.build_css()
        soup = response.bs4()
        cards, _ = self.retry_find(soup, css['detail'])
        log.info(f"{request.url} 当前 {pageNum} 页，卡片数量: {len(cards)}")
        if len(cards) == 0:
            raise Exception(f"{request.url} 第 {pageNum} 页爬取失败，获取cards为0")
        for card in cards:
            url = card.get("href")
            yield feapder.Request(
                url=url,
                method="GET",
                callback=self.parse_detail,
                render=True,
            )

        next_btns, _ = self.retry_find(soup, css['next'])
        if not finished:
            priority = request.priority
            for i in range(len(next_btns) - 1):
                pageNum += 1
                priority += 1
                rep = deepcopy(request)
                rep.params["Npge"] = pageNum
                rep.finished = True
                rep.priority = priority
                yield rep

    def parse_detail(self, request, response):
        if not response.ok:
            response.open()
            raise Exception(f"{request.url}爬取失败")

        css = self.build_css()
        soup = response.bs4()
        imgs, _ = self.retry_find(soup, css['img'])
        for img in imgs:
            srcset = img.get("srcset").strip()
            src = srcset.split("w,")[-1].strip()
            src = src.split(" ")[0].strip()
            title = img.get("alt", False) or img.get("aria-label", False) or ""

            yield SpiderWebImgUrlItem(
                website="jcrew",
                title=title,
                url=src,
            )

    @staticmethod
    def build_css():
        css = {
            "detail": [
                "a.ProductImage__link___uNRia",
            ],
            "next": [
                "select#pagination-select.c-filters__header-item > option",
            ],
            "start": [
                "button.WelcomeMatContainer__button___aixME",
            ],
            "img": [
                "img.RevampedZoomImage__unscaled-image___l7huD"
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


if __name__ == "__main__":
    AigcJcrewSpider().start()
