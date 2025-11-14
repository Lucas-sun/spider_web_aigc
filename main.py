# -*- coding: utf-8 -*-
"""
Created on 2025-10-29 09:09:07
---------
@summary: 爬虫入口
---------
@author: lucas
"""
import os

from feapder import ArgumentParser

from spiders.aigc_jcrew_spider import AigcJcrewSpider
from spiders.aigc_wow_spider2 import AigcWowSpider
from tools.download import Download


def crawl_aigc(args):
    """
    AirSpider爬虫
    """
    if args == 1:
        tasks = [
            AigcJcrewSpider,
        ]
        for task in tasks:
            task().start()
    if args == 2:
        # 下载图片任务
        pass


def crawl_wow(args):
    AigcWowSpider(url_index=args).start()

def download_image(args):
    if args == 1:
        Download().start()
    if args == 0:
        print("测试消息")


if __name__ == "__main__":
    parser = ArgumentParser(description="aigc爬虫")

    parser.add_argument(
        "--crawl_aigc",
        type=int,
        nargs=1,
        help="aigc爬虫",
        choices=[1, 2],
        function=crawl_aigc,
    )
    parser.add_argument(
        "--crawl_wow",
        type=int,
        nargs=1,
        help="aigc爬虫",
        choices=[0, 1, 2, 3, 4, 5],
        function=crawl_wow,
    )

    parser.add_argument(
        "--download_image",
        type=int,
        nargs=1,
        help="下载图片",
        choices=[0, 1],
        function=download_image,
    )

    parser.start()

    # main.py作为爬虫启动的统一入口，提供命令行的方式启动多个爬虫，若只有一个爬虫，可不编写main.py
    # 将上面的xxx修改为自己实际的爬虫名
    # 查看运行命令 python main.py --help
    # AirSpider与Spider爬虫运行方式 python main.py --crawl_xxx
    # BatchSpider运行方式
    # 1. 下发任务：python main.py --crawl_xxx 1
    # 2. 采集：python main.py --crawl_xxx 2
    # 3. 重置任务：python main.py --crawl_xxx 3
