# -*- coding: utf-8 -*-
"""
Created on 2025-11-14 13:44:31
---------
@summary:
1. 从 spider_web_img_url 库里查询下载任务
2. 下发任务，更新任务状态 0:未下载 1:下载完成 -1:下载失败 2:下载中
2. 使用httpx下载图片，保留存储文件地址
3. 下载完成，更新任务下载状态
---------
@author: lucas
"""
import os

import feapder
from feapder import Request, Response
from feapder.db.mysqldb import MysqlDB
from feapder.utils.log import log

from setting import WEBSITE, DOWNLOAD_PATH, MACHINE_DOMAIN


class Download(feapder.AirSpider):
    def __init__(self, thread_count=None):
        super().__init__(thread_count)
        self._mysqldb = MysqlDB()
        self.task_table = "spider_web_img_url"

    def start_requests(self):
        # 从 spider_web_img_url 库里查询下载任务
        sql = f"""
            select * from spider_web_img_url
            where website='{WEBSITE}'
                and status in (0, 2)
            order by created_at asc
        """
        tasks = self._mysqldb.find(sql, to_json=True)
        search = f"""
            select * from {self.task_table}
            where file is not null
            order by created_at desc limit 1
        """
        newest_task = self._mysqldb.find(search, to_json=True)
        if newest_task:
            file = newest_task[0]["file"]
            task_id = int(os.path.basename(file).split(".")[0])
        else:
            task_id = 1
        for task in tasks:
            url = task['url']
            yield feapder.Request(url, task=task, priority=task_id)
            task_id += 1

    def parse(self, request, response):
        """
        下载图片
        :param request:
        :param response:
        :return:
        """
        task = request.task
        task_id = request.priority
        # log.error(f"伪代码 更新任务状态为下载中")
        self._mysqldb.update_smart(self.task_table, {"status": 2}, f"uuid={task['uuid']}")

        if not response.ok:
            raise Exception(f"请求失败 {response.url} {response.status_code}")

        path = DOWNLOAD_PATH
        domain = MACHINE_DOMAIN
        if not path or not domain:
            log.error(f"未设置下载地址或者主机地址，爬虫已停止")
            self.stop_spider()

        path = self.download_path_hack(path, tags=task['tags'])
        image_path = os.path.join(path, f"{str(task_id)}.jpg")
        with open(image_path, "wb") as f:
            f.write(response.content)

        # log.error(f"伪代码 更新任务状态为成功 更新地址为 image_path")
        self._mysqldb.update_smart(self.task_table, {"status": 1, "file": f"{domain}:{image_path}"},f"uuid={task['uuid']}")

    def failed_request(self, request: Request, response: Response, e: Exception):
        task = request.task
        # log.error("伪代码 更新任务状态为失败")
        self._mysqldb.update_smart(self.task_table, {"status": -1}, f"uuid={task['uuid']}")

    def download_path_hack(self, path: str, **kwargs) -> str:
        new_path = path
        os.makedirs(new_path, exist_ok=True)

        # 下载地址处理
        tags: str = kwargs.get("tags", "")
        if tags:
            tag = tags.split(",")[0]
            tlist = tag.split(" ")
            for t in tlist:
                new_path = os.path.join(new_path, t)
            os.makedirs(new_path, exist_ok=True)
        pass

        return new_path


if __name__ == "__main__":
    Download().start()
