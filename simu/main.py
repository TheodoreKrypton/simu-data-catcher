# coding: utf-8

import urllib
import json
import MySQLdb
import bs4
from collections import OrderedDict
from SQLConnection import Connection
import requests
import time
import re
import bs4
import random

UserAgent = []


def read_user_agents():
    global UserAgent
    with open("user_agent.txt") as fp:
        line = fp.readline()
        while line:
            UserAgent.append(line[:-1])
            line = fp.readline()


def get_fund_info_url_part1(page):
    return "http://dc.simuwang.com/Pep/getData.html?page=" + str(page) + "&condition=sort_asc:desc"


def get_fund_info_url_part2(fund_id):
    return "http://dc.simuwang.com/product/" + str(fund_id) + ".html"


def get_net_url(fund_id):
    return "http://dc.simuwang.com/index.php?m=Data&c=Chart&a=jzdb&fund_id=" + fund_id


def get_html(url):
    i = random.randint(0, len(UserAgent)-1)
    headers = {"User-Agent": UserAgent[i]}
    html = requests.get(url, headers=headers).content
    return html


def read_item_from_db(cursor, tbl_name):
    result = {}
    cursor.execute("select * from " + tbl_name)
    res = cursor.fetchall()
    for item in res:
        result[item[1]] = item[0]
    return result


def sql_item(something):
    # get sql formatted representation of something
    if isinstance(something, int) and something == 0:
        return 0
    if not something:
        return "NULL"
    if isinstance(something, str):
        if something[-1] == '%':
            return 0.01 * float(something[:-1])
        else:
            return '\'' + something + '\''
    if isinstance(something, unicode):
        return '\'' + something + '\''
    return something


def store_city_and_advisor_to_db():
    html = get_html(get_fund_info_url_part1(1))
    content = json.loads(html)
    total_page_cnt = content["pager"]["pagecount"]

    with Connection() as conn:
        a = {}
        c = {}
        for i in range(1, total_page_cnt):
            print "[city, advisor]", str(i) + "/" + str(total_page_cnt)

            flag = False
            while not flag:
                try:
                    html = get_html(get_fund_info_url_part1(i))
                    content = json.loads(html)
                    flag = True
                except Exception, ex:
                    print ex

            for fund in content["data"]:
                if not unicode(fund["advisor_id"]) in a and fund["advisor_id"]:
                    a[fund["advisor_id"]] = 0
                    sql = "insert into advisorinfo (advisor_id, advisor_short_name) VALUES " +\
                          "(\'" + unicode(fund["advisor_id"]) + "\'," + "\'" + unicode(fund["advisor"]) + "\')"
                    conn.execute(sql)
                if not unicode(fund["city"]) in c and fund["city"]:
                    sql = "insert into cityinfo (city) VALUES (\'" + unicode(fund["city"]) + "\')"
                    conn.execute(sql)


def store_fund_info_to_db_part1():
    html = get_html(get_fund_info_url_part1(1))
    content = json.loads(html)
    total_page_cnt = content["pager"]["pagecount"]

    with Connection() as conn:
        cities = read_item_from_db(conn.cursor, "cityinfo")
        advisors = read_item_from_db(conn.cusror, "advisorinfo")

        for page in range(1, 1008):
            print "[fund_info_part1]", str(page) + "/" + str(total_page_cnt)

            flag = False
            while not flag:
                try:
                    html = get_html(get_fund_info_url_part1(page))
                    content = json.loads(html)
                except Exception, ex:
                    print ex

            data = content["data"]
            for fund in data:
                info = map(sql_item, [
                    fund["fund_id"],
                    fund["fund_short_name"],
                    fund["fund_type"],
                    fund["register_number"],
                    fund["umbrella_fund"],
                    fund["initial_unit_value"],
                    advisors[unicode(fund["advisor_id"])] if fund["advisor_id"] else None,
                    cities[unicode(fund["city"])] if fund["city"] else None,
                    fund["inception_date"],
                    fund["inception_year"],
                    fund["status_end_date"],
                    fund["liquidate_date"],
                    fund["fund_status"],
                    fund["profession_background"],
                    fund["managers_id"],
                    fund["managers_name"],
                    fund["change_col"]
                ])
                sql = ",".join([unicode(i) for i in info])
                sql = "insert into fundinfo " +\
                      "(fund_id, fund_short_name, fund_type, register_number, umbrella_fund, initial_unit_value," +\
                      "advisor_id, city, inception_date, inception_year, status_end_date, liquidate_date," +\
                      "fund_status, profession_background, managers_id, managers_name, change_col) values ("+sql+")"
                conn.execute(sql)


def store_net_to_db():
    with open("net_log.txt", "w") as fp:
        with Connection() as conn:
            conn.execute("select fund_id from fundinfo")
            all_fund_id = conn.cursor.fetchall()
            all_fund_cnt = len(all_fund_id)
            for index, fund in enumerate(all_fund_id):
                fund_id = fund[0]
                print "[net]", fund_id, str(index) + "/" + str(all_fund_cnt)
                url = get_net_url(str(fund_id))
                try:
                    html = get_html(url)
                    content = json.loads(html)
                    data = content["data"]
                    for day in data:
                        price_date = day["price_date"]
                        price_date = sql_item("20" + price_date)
                        value = day["unit_nav"]
                        conn.execute("select id from fundinfo where fund_id = \'" + str(fund_id) + "\'")
                        _fund_id = str(conn.cursor.fetchone()[0])
                        sql = "insert into netvalue values(" + _fund_id + "," + price_date + "," + value + ")"
                        conn.execute(sql)
                except Exception, ex:
                    print ex
                    fp.write("[net][%s]:%s\n" % (fund_id, str(ex)))
                    conn.execute("select id from fundinfo where fund_id = " + fund_id)
                    _id = conn.cursor.fetchone()
                    _id = _id[0]
                    conn.execute("insert into errorfund_fundinfo (fund_id) values (" + _id + ")")


def update_fundinfo(cursor, col_name, value):
    sql = "update fundinfo set " + col_name + "=" + str(sql_item(value))
    cursor.execute(sql)


def store_fund_info_to_db_part2():
    with open("fund_info_log.txt", "w") as fp:
        with Connection() as conn:
            conn.execute("select fund_id from fundinfo")
            all_fund_id = conn.cursor.fetchall()
            all_fund_cnt = len(all_fund_id)

            disclosure_mark_ptrn = re.compile("disclosure_mark\">(.+?)</span>")
            form_ptrn = re.compile("(<div class=\"f14.+?>封闭期.+?</div> </div>)")
            tag_ptrn = re.compile("<.+?>")
            null_word = ["未设", "保密", "无"]
            num_ptrn = re.compile("(\d+?\.\d+)")

            col_names = [
                "blackout_period",
                "open_day",
                "purchase_starting_point",
                "add_purchase_point",
                "purchase_fee",
                "redemption_fee",
                "warning_level",
                "stop_loss_level",
                "performance_fee",
                "fund_manager",
                "manage_fee",
                "trustee",
                "stock_broker",
                "future_broker",
                "initial_date",
                "register_code",
                "initial_amount",
                "term",
                "is_tier",
                "is_umbrella",
                "production_type"
            ]

            for index, fund in enumerate(all_fund_id):
                fund_id = fund[0]
                print "[fund_info_part2]", fund_id, str(index) + "/" + str(all_fund_cnt)
                url = get_fund_info_url_part2(str(fund_id))
                try:
                    html = get_html(url)
                    html = html.replace("\r\n", " ")

                    disclosure_mark = unicode(re.search(disclosure_mark_ptrn, html).group(1))
                    update_fundinfo(conn.cursor, "disclosure_mark", disclosure_mark)

                    form = re.search(form_ptrn, html).group(0)
                    bs = bs4.BeautifulSoup(form, "lxml")
                    res = bs.findAll({"td"})
                    tmp = []
                    for i, item in enumerate(res):
                        if i % 2:
                            tmp.append(
                                "".join(
                                    re.split(tag_ptrn, str(item))
                                ).strip()
                            )
                    del tmp[8]
                    del tmp[-1]
                    del tmp[-1]

                    # format
                    tmp = map(lambda x: None if x in null_word else x, tmp)

                    try:
                        tmp[2] = float(re.search(num_ptrn, tmp[2]).group(1))
                    except AttributeError, ex:
                        tmp[2] = None

                    try:
                        tmp[3] = float(re.search(num_ptrn, tmp[3]).group(1))
                    except AttributeError, ex:
                        tmp[3] = None

                    if tmp[-3] == "是":
                        tmp[-3] = 1
                    else:
                        tmp[-3] = 0

                    if tmp[-2] == "是":
                        tmp[-2] = 1
                    else:
                        tmp[-2] = 0

                    tmp = map(lambda x: str(sql_item(x)), tmp)
                    sql = [i + "=" + j for i, j in zip(col_names, tmp)]
                    sql = ",".join(sql)
                    sql = "update fundinfo set " + sql + "where fund_id = \'" + str(fund_id) + "\'"
                    conn.execute(sql)

                except Exception, ex:
                    print ex
                    fp.write("[fundinfo][%s]:%s\n" % (fund_id, str(ex)))
                    conn.execute("select id from fundinfo where fund_id = \'" + fund_id + "\'")
                    _id = conn.cursor.fetchone()
                    _id = _id[0]
                    conn.execute("insert into errorfund_net (fund_id) values (" + str(_id) + ")")


def main():
    read_user_agents()

    print "storing cities and advisors ... (1/4)"
    store_city_and_advisor_to_db()

    print "storing fund info (Part 1) ... (2/4)"
    store_fund_info_to_db_part1()

    print "storing net values ... (3/4)"
    store_net_to_db()

    print "storing fund info (Part 2) ... (4/4)"
    store_fund_info_to_db_part2()


if __name__ == '__main__':
    main()
