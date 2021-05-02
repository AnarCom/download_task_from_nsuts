import requests
import json
import base64
import shutil
import tempfile
import itertools as IT
import os

#YOUR DATA HERE
cookies = {
    'experimentation_subject_id': '',
    'CGISESSID': ''}


def rep(path):
    return path.replace("*", "").replace(" ", "_").replace("...", "").replace(":", "").replace("\"", "")


def uniquify(path, sep=''):
    path = path

    def name_sequence():
        count = IT.count()
        yield ''
        while True:
            yield '{s}{n:d}'.format(s=sep, n=next(count))

    orig = tempfile._name_sequence
    with tempfile._once_lock:
        tempfile._name_sequence = name_sequence()
        path = os.path.normpath(path)
        dirname, basename = os.path.split(path)
        filename, ext = os.path.splitext(basename)
        fd, filename = tempfile.mkstemp(dir=dirname, prefix=filename, suffix=ext)
        tempfile._name_sequence = orig
    return filename


res = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Tasks')


def get_dir_for_tour(tour_name):
    return os.path.join(res, tour_name)


def create_dir_for_tour(tour_name):
    return create_dir(get_dir_for_tour(rep(tour_name)))


def get_file_for_task(tour_name, task, ext=".c"):
    return uniquify(os.path.join(get_dir_for_tour(rep(tour_name)), rep(task), "main" + ext))


def folder_exist(path):
    return os.path.exists(path)


def create_folder_for_task(tour_name, task):
    folder = os.path.join(get_dir_for_tour(rep(tour_name)), rep(task))
    print(folder)
    if not os.path.exists(folder):
        os.mkdir(folder)


def create_dir(path):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


if os.path.exists(res):
    shutil.rmtree(res)
create_dir('Tasks')

req = requests.get('https://fresh.nsuts.ru/nsuts-new/api/tours/list', cookies=cookies)
tours_raw = req.content
tours_data = json.loads(tours_raw)
print(tours_data)
for d in tours_data['tours']:
    print(d)
    title = d['title']
    title = title
    create_dir_for_tour(title)
    req = requests.get('https://fresh.nsuts.ru/nsuts-new/api/tours/enter?tour=' + d['id'], cookies=cookies)
    list_of_tasks = requests.get('https://fresh.nsuts.ru/nsuts-new/api/report/get_report', cookies=cookies)
    list_of_tasks = json.loads(list_of_tasks.content)
    for t in list_of_tasks['submits']:
        if t['status'] == '3':
            data = requests.get('https://fresh.nsuts.ru/nsuts-new/api/submit/get_source?id=' + t['id'], cookies=cookies)
            data_for_task = json.loads(data.content)
            # print(data_for_task)
            if '[ET]' in t['task_title']:
                create_folder_for_task(title, t['task_title'])
                tmp_file = get_file_for_task(title, t['task_title'], ".zip.base64")
                tmp_file_z = open(tmp_file, "w")
                tmp_file_z.write(data_for_task['data'])
                tmp_file_z.close()
                file = get_file_for_task(title, t['task_title'], ".zip")
                base64.decode(open(tmp_file), open(file, 'wb'))
            else:
                create_folder_for_task(title, t['task_title'])
                file = get_file_for_task(title, t['task_title'])
                f = open(file, "w", encoding='utf-8')
                for text in data_for_task['text']:
                    s = text
                    cont = base64.b64decode(s.encode('utf8'))
                    cont = cont.decode("UTF-8")
                    f.write(cont)
                f.close()
                print(t)
