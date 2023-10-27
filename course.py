import sys

import requests
import json
import time

Cookie = 'token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvbGV4aWFuZ2xhLmNvbVwvc3VpdGVzXC9hdXRoLWNhbGxiYWNrIiwiaWF0IjoxNjk4Mzc3MDUxLCJleHAiOjE3MDA5NjkwNTEsIm5iZiI6MTY5ODM3NzA1MSwianRpIjoiYWFoTUZmdkhha1N0UGNocSIsInN1YiI6ImI1ZmYyM2Y4YTY0NjExZWE4OGQxNTI1NDAwZWRlZjIxIiwicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsImNvbXBhbnlfaWQiOiIzYzg1MjUwOGE0YjIxMWVhODQ3MzUyNTQwMGVkZWYyMSIsInN0YWZmX3V1aWQiOiJiNWY0YzM3MmE2NDYxMWVhODE0NTUyNTQwMGVkZWYyMSJ9.lgNoUVDTfnV0Fa838z59myluQ2e_3MPy_Okhy7krtwQ; company_server_type=workwechat; company_code=jste; company_old_code=3c851aa4a4b211ea9b18525400edef21; company_display_name=%E6%B1%9F%E8%8B%8F%E6%95%99%E5%B8%88; ti18nLng=zh-CN; XSRF-TOKEN=nlbkwLlwQSzqQxG70ZuJmK7%252BWbqfywm7PrjDK%252BUf4Hps4ZfOiUW0FLKfFkt0gheFTMW7IhpwUv%252B6TYBmjyoHVPf9KiqDJWQQUDHUzlvVipE%253D'


def list_chapter():
    url = "https://jste.lexiangla.com/api/v1/classes/b5e8284467d911eeb0af66f2c73c8c41?with_source_detail=1"
    headers = {
        'Cookie': Cookie,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, verify=False)

    json_data = json.loads(response.text)
    chapters = json_data['data']['chapters']
    ids = []
    for chapter in chapters:
        courses = chapter['courses']
        for course in courses:
            ids.append(course['id'])

    print(ids)
    return ids[:8]


def list_middle_chapter():
    url = "https://jste.lexiangla.com/api/v1/classes/b5e8284467d911eeb0af66f2c73c8c41?with_source_detail=1"
    headers = {
        'Cookie': Cookie,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, verify=False)

    json_data = json.loads(response.text)
    chapters = json_data['data']['chapters']
    ids = []
    titles = []
    for chapter in chapters:
        if chapter['id'] == 359:
            courses = chapter['courses']
            for course in courses:
                titles.append(course['title'])
                ids.append(course['id'])

    print(titles)
    print(ids)
    return ids


def get_time():
    url = "https://jste.lexiangla.com/api/v1/classes/b5e8284467d911eeb0af66f2c73c8c41?with_source_detail=1"
    headers = {
        'Cookie': Cookie,
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, verify=False)

    json_data = json.loads(response.text)
    try:
        learn_time = json_data['data']['pass']['learn_time']
        return learn_time
    except TypeError:
        return 0


def post_msg(event, courses_id):
    url = ('https://jste.lexiangla.com/tapi/class/study/v1/classes/b5e8284467d911eeb0af66f2c73c8c41/courses/'
           + courses_id + '/report-study')

    payload = json.dumps({
        "event": event
    })
    headers = {
        'Cookie': Cookie,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    json_data = json.loads(response.text)
    print(json_data)
    return json_data['data']['status']


def start(courses_id):
    post_msg(1, courses_id)
    print('start:' + courses_id)
    status = 0
    while status == 0:
        status = post_msg(2, courses_id)
        # finish
        if status == 2:
            end(courses_id)
            return
        # 暂停30秒
        time.sleep(30)

    end(courses_id)


def end(courses_id):
    post_msg(3, courses_id)
    print('end:' + courses_id)


def auto():
    learned_time = get_time()
    if learned_time > 400 * 60:
        print('学习完成')
        return

    # 选择课程
    course_ids = list_middle_chapter()
    # course_ids = list_chapter()

    for courses_id in course_ids:
        # 终止一次全部课程防止重复学习
        end(courses_id)

    for courses_id in course_ids:
        start(courses_id)
        learned_time = get_time()
        if learned_time > 400 * 60:
            print('学习完成')
            return


if __name__ == '__main__':
    # start('52450a12682111eeae869ab385c8785b')
    # list_middle_chapter()
    auto()
