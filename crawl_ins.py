
# 爬取 instagram.com
from html.parser import HTMLParser
from lxml.html import tostring
from mysql_pool import get_db_pool
from threading import RLock
from lxml import etree
import requests
import oss2
import time
import threading
import re
import random
from proxy_aby import proxies
import json
import imghdr
import urllib.parse

auth = oss2.Auth('LTAIy1CkOq4y07J1', 'hnIIIHXuQOIwmc0J50dtgMLamlYyAC')
endpoint = 'oss-cn-shanghai.aliyuncs.com'

lock = threading.Lock()

global localpath
# localpath = 'C:\\Users\\wsh\\Desktop\\img\\'
localpath = 'C:\\Users\\DELL\\Desktop\\test\\'

query_hash_data = '32b14723a678bd4628d70c1f877b94c9'


def trans(text):
    url = "http://139.196.47.220/api/znzgo/crawlRecord/trans?text="+text
    try:
        res = requests.Session().get(url)
    except:
        raise TypeError
    if res.status_code == 200:
        html = res.text
        return html


def put_img_on_qingtu(imgname):
    bucket = oss2.Bucket(auth, endpoint, 'qingtu-image-originals')
    print('上传:', imgname)
    with open(localpath+imgname, 'rb') as f:
        content = f.read()
    return bucket.put_object('instr/'+imgname, content)

class EdyIns(object):
    def __init__(self):
        cookies = 'ds_user_id=47760242685;csrftoken=mq0i5DGVCFQxVKfbP14ORJA4WDGI9EHN;rur=ASH;sessionid=47760242685%3AMIkQrIG31d5XZa%3A7;ig_nrcb=1;ig_did=D2F12B5D-E1C0-4E6A-B694-A0BD66DE9AD5;mid=YHaxvQALAAG75cFnd1TIGujHQYpU;'

        requests.packages.urllib3.disable_warnings()
        self.session = requests.Session()
        self.session.verify = False
        self.mysql = get_db_pool(True)
        self.lock = RLock()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            # 'x-requested-with': 'XMLHttpRequest'
            'Cookie': cookies
        }
        self.flag = None
        self.session.proxies = proxies
        self.count = 0
        # self.host = 'https://www.yutu.cn/'
        self.cookies = cookies
        self.third_tuple = set()

     # 获取设计师和标签对应列表

    def get_designer_list(self):
        conn = self.mysql.connection()
        cursor = conn.cursor()
        cursor.execute(
            'select id,designer,tag from inspiration_crawl_instagram where status is null  ')
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        if result:
            return result
        else:
            return []

      # 修改状态

    def update_status(self, designer):
        conn = self.mysql.connection()
        cursor = conn.cursor()
        cursor.execute(
            'update inspiration_crawl_instagram set status = 1  where designer=%s', [designer])
        conn.commit()
        conn.close()
        return ''

    # 主方法
   # @ retry(stop_max_attempt_number=1, wait_fixed=3000)
    def get_List(self, designer, tag):

        url = "https://www.instagram.com/"+designer+"/"

        try:
            res = self.session.get(url)
        except:
            raise TypeError

        if res.status_code == 200:
            # html = res.text.encode('ISO-8859-1').decode('utf-8')
            html = res.text

            # with open(localpath+'test.html', 'w', encoding='utf-8') as f:
            #     f.write(html)

            # element = etree.HTML(html)
            local = re.findall(
                r'<script type="text/javascript">window._sharedData = (.*);</script>', html)
            # print(local[0])
            text = json.loads(local[0])
            entry_data = text['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
            pageid = text['entry_data']['ProfilePage'][0]['graphql']['user']['id']
            end_cursor = text['entry_data']['ProfilePage'][0]['graphql']['user'][
                'edge_owner_to_timeline_media']['page_info']["end_cursor"]

            print("pageid", pageid)
            print("end_cursor", end_cursor)
            for i in entry_data:
                imgurl = i['node']['display_url']
                imgId = i['node']['id']
                height = i['node']['dimensions']['height']
                width = i['node']['dimensions']['width']

                if height <= 400 and width <= 400:
                    continue
                title = i['node']['edge_media_to_caption']['edges'][0]['node']['text']
                title = title.replace("\n", " ")
                shortcode = i['node']['shortcode']
                tags = {"tags": self.get_detail(shortcode)}

                obj = self.save_img(imgId, imgurl, url).resp.response.url.replace(
                    'http://qingtu-image-originals.oss-cn-shanghai.aliyuncs.com', 'https://image.znzgo.com')
                print(obj)
                rdata = {}
                rdata['title'] = title
                rdata['img'] = obj
                rdata['width'] = width
                rdata['height'] = height
                rdata['third_id'] = imgId
                rdata['data_json'] = str(tags)
                rdata['url'] = imgurl
                self.save_data(rdata)

            self.get_ListBypage(
                query_hash_data, pageid, end_cursor)

        return True

    def get_ListBypage(self, query_hash, id, after):
        url = 'https://www.instagram.com/graphql/query/?'
        data = 'query_hash='+query_hash+'&variables='
        variables = '{"id":"'+str(id)+'","first":12,"after":"'+after+'"}'
        data2 = data+str(variables)
        url = url + data2

        try:
            res = self.session.get(url)
        except:
            raise TypeError

        if res.status_code == 200:
            # html = res.text.encode('ISO-8859-1').decode('utf-8')
            html = res.text
            # with open(localpath+'test2.json', 'w', encoding='utf-8') as f:
            #     f.write(html)
            text = json.loads(html)
            entry_data = text['data']['user']['edge_owner_to_timeline_media']['edges']
            pageid = ''
            end_cursor = text['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
           # ['edge_owner_to_timeline_media']
            # ['page_info']["end_cursor"]

            has_next_page = text['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']

            print("pageid", pageid)
            print("end_cursor", end_cursor)
            for i in entry_data:
                imgurl = i['node']['display_url']
                imgId = i['node']['id']
                height = i['node']['dimensions']['height']
                width = i['node']['dimensions']['width']
                pageid = i['node']['owner']['id']
                if height <= 400 and width <= 400:
                    continue
                obj = self.save_img(imgId, imgurl, url).resp.response.url.replace(
                    'http://qingtu-image-originals.oss-cn-shanghai.aliyuncs.com', 'https://image.znzgo.com')

                title = i['node']['edge_media_to_caption']['edges'][0]['node']['text']
                title = title.replace("\n", " ")

                shortcode = i['node']['shortcode']
                tags = {"tags": self.get_detail(shortcode)}

                rdata = {}
                rdata['title'] = title
                rdata['img'] = obj
                rdata['width'] = width
                rdata['height'] = height
                rdata['third_id'] = imgId
                rdata['data_json'] = str(tags)
                rdata['url'] = imgurl
                self.save_data(rdata)

            print("has_next_page", has_next_page)

            if has_next_page:
                self.get_ListBypage(query_hash_data, pageid, end_cursor)

        return True

    def get_detail(self, shortcode):
        url = 'https://www.instagram.com/p/'+shortcode+'/'
        try:
            res = self.session.get(url)
        except:
            raise TypeError

        if res.status_code == 200:
            # html = res.text.encode('ISO-8859-1').decode('utf-8')
            html = res.text
            # with open(localpath+'test3.html', 'w', encoding='utf-8') as f:
            #     f.write(html)

            headstr = "<script type=\"text/javascript\">window.__additionalDataLoaded[\'(\'/p/" + \
                shortcode + \
                "/\',(.*);</script>"

            local = re.findall(
                r'<script type=\"text/javascript\">window.__additionalDataLoaded(.*);</script>', html)

            str1 = local[0].replace("('/p/"+shortcode+"/',", "")

            str1 = str1.rstrip(')')
            text = json.loads(str1)[
                'graphql']['shortcode_media']['edge_media_to_parent_comment']['edges'][0]['node']['text'].replace('#', '')
            # with open(localpath+'detail.json', 'w', encoding='utf-8') as f:
            #     f.write(str(str1))
            resultList = []
            for i in text.split(' '):
                resultList.append(trans(i))
            return resultList

    def save_img(self, imgId, url, referer):
        self.session.headers['referer'] = referer
        try:
            res = self.session.get(url)
            imgtype = imghdr.what(None, res.content)
            # print(imgtype)
            if imgtype == 'jpeg':
                imgtype = 'jpg'

            strlist = ['jpg', 'jpeg', 'png', 'webp']

            if any(imgtype in s for s in strlist):
                imgname = str(imgId) + "." + imgtype
                with open(localpath+imgname, 'wb') as f:
                    f.write(res.content)
                return put_img_on_qingtu(imgname)
                print('保存成功')
            else:
                print(imgtype+"不在保存列表中")

        except Exception as error:
            print(error)
            print('保存失败')
        return ''

    def save_data(self, data):
        conn = self.mysql.connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''insert into inspiration_ins_crawling
                        (title_origin,title_translated,cover,img_small,img_origins,
                        width_cover,height_cover,width_small,height_small,width_origins,
                        height_origins,type,source,third_id,data_json,
                        crawl_url) values
                        (%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,
                        %s) ''',
                        [data['title'], trans(data['title']), data['img'], data['img'], data['img'],
                            data['width'], data['height'], data['width'],  data['height'], data['width'],
                            data['height'], '1', 'instagram', data['third_id'], data['data_json'], data['url']])
        except Exception as error:
            print(error)

        conn.commit()
        conn.close()
        return True


def start():
    ins = EdyIns()

    list1 = ins.get_designer_list()

    for i in list1:
        print(i)
        ins.get_List(i[1], i[2])


if __name__ == '__main__':
    pass
    #start()
