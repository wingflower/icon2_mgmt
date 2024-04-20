#!/usr/bin/env python3
import ray
import asyncio
import requests
import pymysql
import argparse
import time

from datetime import datetime


def get_parser():
    parser = argparse.ArgumentParser(prog='Async Check Url')
    parser.add_argument('--db_host', type=str, help=f'')
    parser.add_argument('--db_pw', type=str, help=f'')
    parser.add_argument('--db_user', type=str, help=f'')
    parser.add_argument('--db_name', type=str, help=f'')
    parser.add_argument('--check_term', type=int, help=f'', default=60)
    return parser.parse_args()


class AsyncCheckUrl:
    def __init__(self, args):
        ray.init()
        self.args = args
        self.db_conn = pymysql.connect(
            host=self.args["db_host"],
            user=self.args["db_user"],
            password=self.args["db_pw"],
            db=self.args["db_name"],
            charset="utf8"
        )
        self.cur = self.db_conn.cursor()

    def _select_urls(self, ):
        sql = "select * from check_urls"
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        return rows

    def _insert_ursl(self, rs):
        sql = "insert into status_urls (url_id, state) values (%s, %s)"
        insert_data = [(key, val) for key, val in rs.items()]
        self.cur.executemany(sql, insert_data)
        return self.cur

    async def check_url(self, url_info):
        _start = datetime.now()
        _start_str = _start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        try:
            response = requests.head(url_info["url"], verify=False)
            _end = datetime.now()
            if response.status_code == 200:
                return "running", url_info["url"], _start_str, _end - _start, url_info["id"]
            else:
                return "stopped", url_info["url"], _start_str, _end-_start, url_info["id"]
        except Exception as e:
            return "stopped", url_info["url"], _start_str, 0, url_info["id"]

    async def gather_rs(self, urls):
        _ = await asyncio.gather(
            *[self.check_url(url_info) for url_info in urls]
        )

    def run(self, ):
        urls = self._select_urls()
        while True:
            asyncio.run(self.gather_rs(urls))


if __name__ == "__main__":
    args = vars(get_parser())
    ACU = AsyncCheckUrl(args)
    ACU.run()