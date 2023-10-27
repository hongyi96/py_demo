import sys

import requests
import json
import time

Cookie = 'company_server_type=workwechat; company_code=jste; company_old_code=3c851aa4a4b211ea9b18525400edef21; company_display_name=%E6%B1%9F%E8%8B%8F%E6%95%99%E5%B8%88; ti18nLng=zh-CN; token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvbGV4aWFuZ2xhLmNvbVwvc3VpdGVzXC9hdXRoLWNhbGxiYWNrIiwiaWF0IjoxNjk3OTYyOTgxLCJleHAiOjE3MDA1NTQ5ODEsIm5iZiI6MTY5Nzk2Mjk4MSwianRpIjoiaDR4cER4UjdiVVJpTW81MyIsInN1YiI6IjY4ZmZhYTM4MTUzNDExZWNhZTc5MTY4NjRiYzYzYTg2IiwicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsImNvbXBhbnlfaWQiOiIzYzg1MjUwOGE0YjIxMWVhODQ3MzUyNTQwMGVkZWYyMSIsInN0YWZmX3V1aWQiOiI2OGVhZmE3YTE1MzQxMWVjYjg2NzE2ODY0YmM2M2E4NiJ9.23p6y1voYw8cdLKMeewNDPWqG8KyVogn1gHlesogDGk; XSRF-TOKEN=vVRBsMP6sDrjp69aGGRkt%252Bz7biBSaHnNmVdb8tNoCepHkn4XexVAMTEjYP3%252FrCqcDkMnirkFZ37sScFnhdoddXZ9%252FQ01fvJOPShXtLPwcVM%253D'


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
    course_ids = list_chapter()

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
    auto()
