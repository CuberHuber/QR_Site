import os
import json
from math import ceil
from hashlib import sha256

import werkzeug
from flask import render_template, redirect, url_for, request, flash, \
    send_from_directory, session, make_response
from flask_login import login_user, login_required, UserMixin
import flask_login
import requests
from werkzeug.utils import secure_filename

from qr_site import app, ALLOWED_EXTENSIONS
from qr_site.models import User

numbers_page = []
action_number_page = 0

exp_valid = ['jpg', 'png', 'bmp']
_id_to_img = {}
users_log = {

}


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route("/", methods=['GET'])
def index():
    global numbers_page
    global action_number_page
    # ЗАПРОС ИЗ БД ВСЕХ ИВЕНТОВ
    # with open("qr_site/"+url_for('static', filename='js/content.json'), 'r', encoding="utf-8") as json_data:
    #     events = json.load(json_data)
    response = get_all_events()
    id_events = response[0]
    events = response[1]

    _id_to_img = get_image_of_events(id_events)

    amount_page = ceil(events['count']/5)
    print(amount_page)
    numbers_page = []
    for page in range(1, amount_page+1):
        if page <= 5:
            numbers_page.append(page)
        else:
            break
    print(numbers_page)
    action_number_page = 0

    len_list_page = len(numbers_page)
    print(amount_page, numbers_page, events['count'])
    user = get_current_user()
    print(user)
    if user.status_code == 200:
        is_user = user.json().get('user')
        print(is_user)
    else:
        is_user = False
    return render_template("index.html", page_title="Главная", events=events, amount_page=amount_page,
                           numbers_page=numbers_page, action_number_page=action_number_page, len_list_page=len_list_page,
                           user=is_user, id_events=id_events, _id_to_img=_id_to_img)


@app.route("/events/<_page>", methods=['GET'])
def pages(_page):
    global numbers_page
    global action_number_page
    print('page', _page)
    # ЗАПРОС ИЗ БД ВСЕХ ИВЕНТОВ
    # coco = session['cookie']
    # print( coco)
    # response = requests.get('http://80.78.245.132:5000/api/v2.0/get-current-user', cookies=request.cookies)
    # print(response)

    # print(session['user_id'])
    # with open("qr_site/"+url_for('static', filename='js/content.json'), 'r', encoding="utf-8") as json_data:
    #      events = json.load(json_data)

    response = get_all_events()
    id_events = response[0]
    events = response[1]
    _id_to_img = get_image_of_events(id_events)

    amount_page = ceil(events['count']/5)
    print(amount_page)
    # numbers_page = [page for page in range(1, amount_page+1 or 6)]
    print(numbers_page, events['count'])
    #action_number_page = int(_page)-1
    _page = int(_page)
    if amount_page > 5:
            if action_number_page == 0:
                pass
            else:
                if action_number_page > (_page - 1):
                    # ЕСЛИ ВЫБРАННАЯ СТРАНИЦА МЕНЬШЕ ЧЕМ АКТИВНАЯ
                    for i in range(len(numbers_page)):
                        numbers_page[i] -= action_number_page - _page + 1
                    print(numbers_page)
                    for i in range(len(numbers_page), 0, -1):
                        print(numbers_page[i - 1])
                        if numbers_page[i - 1] <= 0:
                            numbers_page.pop(numbers_page[i - 1])

                    if len(numbers_page) < 5:
                        for i in range(len(numbers_page) + 1, 6):
                            numbers_page.append(i)

                        pass
                elif action_number_page < (_page - 1):
                    # ЕСЛИ ВЫБРАННАЯ СТРАНИЦА БОЛЬШЕ ЧЕМ АКТИВНАЯ
                    for i in range(len(numbers_page)):
                        numbers_page[i] += _page - action_number_page - 1
                    print(numbers_page)
                    for i in range(len(numbers_page), 0, -1):
                        print(numbers_page[i - 1])
                        if numbers_page[i - 1] > amount_page:
                            numbers_page.pop(i - 1)
                    if len(numbers_page) < 5:
                        for i in range(amount_page-len(numbers_page), amount_page - 5, -1):
                            numbers_page.insert(0, i)

                else:
                    pass


    action_number_page = _page - 1
    len_list_page = len(numbers_page)
    print(numbers_page, action_number_page)

    print(amount_page, numbers_page)
    user = get_current_user()
    print(user)
    if user.status_code == 200:
        is_user = user.json().get('user')
        privilege_id = user.json().get('privilege_id')
        print(is_user, privilege_id)
    else:
        is_user = False
    # events = events['response']
    return render_template("index.html", page_title="Главная", events=events, amount_page=amount_page,
                           numbers_page=numbers_page, action_number_page=action_number_page, len_list_page=len_list_page,
                           user=is_user, id_events=id_events, _id_to_img=_id_to_img)
    pass


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/inner_file", methods=['GET', 'POST'])
def innerfile():
    if request.method == "POST":
        file = request.files.get('file')
        print(file)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('innerfile', filename=filename))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    global users_log
    email = request.form.get('email')
    password = request.form.get('password')

    if request.method == 'POST':
        if email == "" or password == "":
            flash('Заполните все поля')
        else:
            # ЗАПРОС НА v.1.0

            pas = sha256(password.encode('utf-8')).hexdigest()

            log_request = {
                'email': str(email),
                'password': str(pas)
            }

            response = requests.post("http://80.78.245.132:5000/api/v2.0/login", json=log_request)
            # db_user = db.session.query(Users).filter_by(email=log_request['email'],
            #                                               password=log_request['password']).first()
            print(response, response.status_code, response.cookies, response.json())
            if response.status_code == 200:
                # user = User((response.json()).get('id'), response.cookies)
                if response.json().get('status') == 'USER NOT FOUND':
                    flash('Пользователь не найден')
                    pass
                else:
                    render = make_response(redirect(url_for('index')))
                    render.set_cookie('session', response.cookies['session'])
                    requests.get("http://80.78.245.132:5000/api/v2.0/create-visitor-self", cookies=response.cookies)
                    return render
            else:
                flash('Какая-то ошибка')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        radio = request.form.get('radio')
        email = request.form.get('email')
        first_name = request.form.get('firstname')
        second_name = request.form.get('secondname')
        last_name = request.form.get('lastname')
        password = request.form.get('password1')
        password2 = request.form.get('password2')

        if radio == "" or email == "" or first_name == "" or second_name == "" or password == "" or password2 == "":
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            # Здесь должна быть запись в БД
            # перед этим обязательно!!! ЗАШИФРОВАТЬ ДАННЫЕ

            if radio == "mem":
                privilege_level = 3
            elif radio == "org":
                privilege_level = 2

            pas = sha256(password.encode('utf-8')).hexdigest()


            # ЗАПРОС НА API v.2.0
            # Словарь запроса регистрации на v.1.0
            reg_request = {
                'name': str(first_name),
                'surname': str(second_name),
                'email': str(email),
                'password': str(pas),
                'privilege_id': str(privilege_level)
            }
            if last_name != "":
                reg_request['patronymic'] = last_name
                pass

            response_v1_0 = requests.post('http://80.78.245.132:5000/api/v2.0/register', json=reg_request)

            if response_v1_0.status_code == 200:
                return redirect(url_for('login_page'))
            elif response_v1_0.status_code >= 500 and response_v1_0.status_code < 600:
                flash('Извините. какие-то проблемы с сервисом')
            elif response_v1_0.status_code == 400:
                if response_v1_0.json().get('status') == 'EMAIL ALREADY EXISTS':
                    flash('Такая почта уже зарегистрирована')
                else:
                    flash('Неизвестная ошибка сервера. пожалуйста перезагрузите страницу')

            print(response_v1_0.reason)
            print(response_v1_0.json())
            # Проверка корректности введенных данных
            print(radio, email, first_name, second_name, last_name, password, password2)
            return render_template('register.html')
    else:
        return render_template('register.html')


# ПОКА НЕ РАБОТАЕТ
@app.route('/api/reg-on-event', methods=['POST'])
def registration_on_event():
    # response = get_current_user()
    #
    #
    # if response.status_code == 200:
    #     # Пользователь зареган
    #
    #     pass
    # elif response.status_code == 401:
    #     # ощибка логина
    #     pass
    name = request.form.get('name')
    second_name = request.form.get('second_name')
    role = request.form.get('role')
    image = request.form.get('files[]')
    email = request.form.get('email')
    print(name, second_name, role, email)
    print(image)
    response = requests.get('http://80.78.245.132:5000/api/v2.0/create-visitor-self', cookies=request.cookies)
    if response.status_code == 200 or response.status_code == 400:
        # Создание визитора
        print('визитор создан')

        pass
    else:
        print('какие-то проблемы')

    return redirect(url_for('index'))


@app.route('/api/logout', methods=['GET'])
def logout():
    print('ВЫХОД')
    response = requests.get('http://80.78.245.132:5000/api/v2.0/logout', cookies=request.cookies)
    render = make_response(redirect(url_for('index')))
    # print(response.cookies)
    render.set_cookie('session', '', expires=0)
    # print(request.cookies)
    if response.status_code == 200:
        # print(response.json())
        # print(response.cookies)
        pass
    return render


@app.route('/create-code-simple', methods=['POST'])
def add_user_on_event():
    event_id = request.form.get('id_event')
    print('id_event: ', event_id)
    response = requests.post('http://80.78.245.132:5000/api/v2.0/create-code-simple', json={'id': str(event_id)}, cookies=request.cookies)

    if response.status_code == 401:
        return redirect(url_for('login_page'))

    return redirect(url_for('index'))


@app.route('/add-referral-link', methods=['POST'])
def add_referral_link():

    name = request.form.get('name')
    surname = request.form.get('second_name')
    lastname = request.form.get('last_name')
    event_id = request.form.get('id-event')
    email = request.form.get('email')
    # print('event_id- ', event_id)

    x = {
        'name': name,
        'surname': surname,
        'email': email
    }

    visitor = requests.post('http://80.78.245.132:5000/api/v2.0/create-visitor-ref', json=x, cookies=request.cookies)

    if visitor.status_code == 200:
        visitor_id = visitor.json().get('visitor_id')
        obj=request.files.get('files')
        file = werkzeug.datastructures.FileStorage(obj)
        # print(visitor_id)
        # print(obj.filename)
        # print(obj.stream)
        # print(obj.mimetype)
        if obj.filename.split('.')[-1] in exp_valid:
            response = requests.post('http://80.78.245.132:5000/api/v2.0/upload-photo-ref', files={'file': (obj.filename, obj.stream, obj.mimetype)},
                          data={'id': str(visitor_id), 'type': 'visitors'}, cookies=request.cookies)

            requests.post('http://80.78.245.132:5000/api/v2.0/create-code-simple', json={'id': str(event_id), 'visitor_id': str(visitor_id)}, cookies=request.cookies)
        else:
            flash('не подходящее разрешение фотографии')


    else:
        # print('not log in')
        # переход на логин
        return redirect(url_for('login_page'))

    return redirect(url_for('index'))


@app.route('/add-new-user-for-event', methods=['POST'])
def add_new_user_for_event():

    name = request.form.get('name')
    surname = request.form.get('second_name')
    patronymic = request.form.get('last_name')

    event_id = request.form.get('id-event')

    send_copy = request.form.get('send_copy')

    email = request.form.get('email')

    image = request.files.get('files')
    print(send_copy, event_id, image)
    if "" in [name, surname, event_id, email, image.filename]:

        new_user = {
            'name': name,
            'surname': surname,
            'event_id': event_id,
            'send_copy': send_copy,
            'email': email,
        }
        if patronymic != "":
            new_user['patronymic'] = patronymic

        visitor = requests.post('http://80.78.245.132:5000/api/v2.0/create-visitor-ref', json=new_user, cookies=request.cookies)

        if visitor.status_code == 200:
            visitor_id = visitor.json().get('visitor_id')
            if image.filename.split('.')[-1] in exp_valid:
                response = requests.post('http://80.78.245.132:5000/api/v2.0/upload-photo-ref', files={'file': (image.filename, image.stream, image.mimetype)},
                              data={'id': str(visitor_id), 'type': 'visitors'}, cookies=request.cookies)

                requests.post('http://80.78.245.132:5000/api/v2.0/create-code-simple', json={'id': str(event_id), 'visitor_id': str(visitor_id)}, cookies=request.cookies)
            else:
                flash('не подходящее разрешение фотографии')
        else:
            # print('not log in')
            # переход на логин
            # return redirect(url_for('login_page'))
            pass
    else:
        # print('event_id- ', event_id)
        flash('заполните поля или добавте фото')

    messages = json.dumps({"event_id": event_id})
    session['messages'] = messages
    return redirect(url_for('event_page', json=json.dumps({'event_id': event_id})), code=307)

@app.route('/profile', methods=['GET', 'POST'])
def organizer_profile():
    event = None
    image_path = None
    visitors = None
    current_event_id = None
    # select-event: 200

    # event_image
    #visitors


    print(request.method)
    if request.method == 'POST':
        type = request.form.get('type-request')
        print(type)
        if type == 'create':
            # СОЗДАНИЕ МЕРОПРИЯТИЯ
            name_event = request.form.get('title')
            description_event = request.form.get('description')
            datetime_start = request.form.get('datetime_start')
            datetime_end = request.form.get('datetime_end')

            image = request.files.get('files')
            print(image, f'name: {image.filename}')
            print(type)

            if "" in [name_event, description_event, datetime_start, datetime_end, image.filename]:
                # не заполненная форма
                flash('заполните пустые поля или добавьте фото', category='error')
                return redirect(url_for('organizer_profile'))
            else:
                # заполненная форма
                datetime_start = datetime_start.replace('T', ' ') + ':00.000000'
                datetime_end = datetime_end.replace('T', ' ') + ':00.000000'

                print(datetime_start)
                print(datetime_end)
                print(name_event)
                print(description_event)
                _json = {
                    "name": name_event,
                    "description": description_event,
                    "datetime_start": datetime_start,
                    "datetime_end": datetime_end
                }
                # создание мероприятия
                new_event = requests.post('http://80.78.245.132:5000/api/v2.0/create-event',
                                           json=_json, cookies=request.cookies)

                print(new_event)
                if new_event.status_code == 200:
                    event_id = new_event.json().get('event_id')
                    response = requests.post('http://80.78.245.132:5000/api/v2.0/upload-photo', files={'file': (image.filename, image.stream, image.mimetype)},
                          data={'id': str(event_id), 'type': 'events'}, cookies=request.cookies)
                else:
                    redirect(url_for('organizer_profile'))


        elif type == 'create-security':
            name = request.form.get('name')
            surname = request.form.get('surname')
            patronymic = request.form.get('patronymic')
            email = request.form.get('email')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            image = request.files.get('files')
            print(image)
            if "" in [name, surname, email, email, password1, password2, image.filename]:
                flash('заполните постые поля или загрузите фото', category='error')
            elif password1 != password2:
                flash('пароли не совпадают', category='error')
            else:
                reg_security= {
                    'name': str(name),
                    'surname': str(surname),
                    'email': str(email),
                    'password': str(password1),
                    'privilege_id': '1'
                }
                if patronymic != "":
                    reg_security['patronymic'] = patronymic
                user_security = requests.post('http://80.78.245.132:5000/api/v2.0/create-user', json=reg_security,
                                              cookies=request.cookies)
                if user_security.status_code == 200:
                    security_id = user_security.json().get('user_id')

                    response = requests.post('http://80.78.245.132:5000/api/v2.0/upload-photo', files={'file': (image.filename, image.stream, image.mimetype)},
                          data={'id': str(security_id), 'type': 'users'}, cookies=request.cookies)
                else:
                    flash('Данный пользователь уже зарегистрирован', category='error')
                    return redirect(url_for('organizer_profile'))
                #
            redirect(url_for('organizer_profile'))
            pass
        elif type == '200':
            #вывод 1 выбранного мероприятия
            event_id = request.form.get('event_id')
            print(event_id)
            event = requests.post('http://80.78.245.132:5000/api/v2.0/get-event', json={'id': str(event_id)},
                                  cookies=request.cookies)
            print(event)
            if event.status_code == 200:
                event = event.json()
                print('event: ',event)
                image = requests.get('http://80.78.245.132:5000/api/v2.0/get-event-photo', json={'id': str(event_id)})
                if image.status_code == 200:
                    image_name = str(event_id)
                    extension = (image.headers['Content-Disposition'].split('.'))[-1]
                    image_name += '.' + extension

                    img = open(os.path.abspath('qr_site/static/img_background_event')+'/'+image_name, 'wb')
                    img.write(image.content)
                    img.close()
                    # print(image_name)
                else:
                    image_name = "anonimus_image.jpg"
                    # print(image_name)

                image_path = '/static/img_background_event/' + image_name
                print(image_path)

                visitors = requests.post('http://80.78.245.132:5000/api/v2.0/get-visitors-for-event',
                                     json={'id': str(event_id)}, cookies=request.cookies)
                visitors = visitors.json()
                current_event_id = event_id
                print(visitors)
            pass
        elif type == 'create-user':
            name = request.form.get('name')
            surname = request.form.get('second_name')
            patronymic = request.form.get('last_name')

            event_id = request.form.get('id-event')

            role = request.form.get('role')

            send_copy = request.form.get('send_copy')

            email = request.form.get('email')

            image = request.files.get('files')
            print(name, surname, event_id, email, image.filename)
            if "" in [name, surname, event_id, email, image.filename]:
                # print('event_id- ', event_id)
                print('проеб')
                flash('заполните поля или добавте фото')
                redirect(url_for('organizer_profile'))
            else:
                new_user = {
                    'name': name,
                    'surname': surname,
                    # 'event_id': event_id,
                    # 'send_copy': send_copy,
                    'email': email,
                    'role_id': role
                }
                if patronymic != "":
                    new_user['patronymic'] = patronymic

                visitor = requests.post('http://80.78.245.132:5000/api/v2.0/create-visitor', json=new_user, cookies=request.cookies)

                if visitor.status_code == 200:
                    visitor_id = visitor.json().get('visitor_id')
                    print(visitor_id)
                    if image.filename.split('.')[-1] in exp_valid:
                        response = requests.post('http://80.78.245.132:5000/api/v2.0/upload-photo', files={'file': (image.filename, image.stream, image.mimetype)},
                                      data={'id': str(visitor_id), 'type': 'visitors'}, cookies=request.cookies)

                        print('event-id --->>', event_id)
                        response = requests.post('http://80.78.245.132:5000/api/v2.0/create-code-simple', json={'id': str(event_id), 'visitor_id': str(visitor_id)}, cookies=request.cookies)
                        print(response, response.reason)
                    else:
                        flash('не подходящее разрешение фотографии')
                else:
                    # print('not log in')
                    # переход на логин
                    # return redirect(url_for('login_page'))
                    pass





    user = requests.get('http://80.78.245.132:5000/api/v2.0/get-current-user', cookies=request.cookies)
    if user.status_code == 200:
        print(user.json())
        if user.json().get('user').get('privilege_id') in [0, 2]:
            # Пользователь зарегистрирован и он является организатором
            user = user.json().get('user')
            image_user = requests.post('http://80.78.245.132:5000/api/v2.0/get-photo',
                          json={"id": str(user.get('id')), "type": "users"}, cookies=request.cookies)
            if image_user.status_code == 200:
                # есть картинка
                image_name = str(user.get('id'))
                extension = (image_user.headers['Content-Disposition'].split('.'))[-1]
                image_name += '.' + extension
                print(image_name)
                img = open(os.path.abspath('qr_site/static/user_image')+'/'+image_name, 'wb')
                img.write(image_user.content)
                img.close()
                pass
            else:
                image_name = 'anonim-user.jpg'
                pass

            user_image = '/static/user_image/'+image_name

            created_events = requests.get('http://80.78.245.132:5000/api/v2.0/get-created-events', cookies=request.cookies)

            print(created_events.status_code)

            list_events = created_events.json()
            print(list_events)

            return render_template('organizer-profile.html', user=user, user_image=user_image, list_events=list_events,
                                   seleced_event=event, event_image=image_path, visitors=visitors, current_event_id=current_event_id)
        else:
            # переход на поле логина
            return redirect(url_for('login_page'))
        pass
    else:
        return redirect(url_for('login_page'))


@app.route('/event-page', methods=['POST'])
def event_page():
    print(request)
    try:
        print(request.get_json())
    except:
        pass
    event_id = request.form.get('event_id')

    print('id_event: ', event_id)
    x = {
        'id': str(event_id)
    }
    event = requests.post('http://80.78.245.132:5000/api/v2.0/get-event', json=x, cookies=request.cookies)
    print(event)
    if event.status_code == 200:
        # все хорошо
        print(event.json())
        event = event.json()
        image = requests.get('http://80.78.245.132:5000/api/v2.0/get-event-photo', json={'id': str(event_id)})
        if image.status_code == 200:
            image_name = str(event_id)
            extension = (image.headers['Content-Disposition'].split('.'))[-1]
            image_name += '.' + extension
            img = open(os.path.abspath('qr_site/static/img_background_event')+'/'+image_name, 'wb')
            img.write(image.content)
            img.close()
            # print(image_name)
        else:
            image_name = "anonimus_image.jpg"
            # print(image_name)

        image_path = '/static/img_background_event/' + image_name
        print(image_path)

        visitors = requests.post('http://80.78.245.132:5000/api/v2.0/get-visitors-for-event',
                                 json={'id': str(event_id)}, cookies=request.cookies)
        if visitors.status_code == 200:
            # все хорошо
            visitors = visitors.json()
            print(visitors)

            return render_template('settings-event.html', event=event, image=image_path, visitors=visitors, event_id=event_id)
        else:
            # пиздец все плохо
            pass
    else:
        #все плохо
        pass

    return redirect(url_for('organizer_profile'))


@app.route('/add-events', methods=['GET'])
def add_events():

    #send_copy                                      !!!!!!!!!!!!!!!!

    pass


def get_all_events():
    """ Получение всех элементов """
    response = requests.get('http://80.78.245.132:5000/api/v2.0/get-events')

    events = response.json()
    id_events = []
    for event in events['events']:
        id_events.append(event['id'])
    print(events)
    print(id_events)
    return id_events, events


def get_image_of_events(id_events):
    """
    запрашивает и сохраняет
    """
    id_path_img = {}
    for id_event in id_events:
        x = {
            'id': str(id_event)
        }
        response = requests.get('http://80.78.245.132:5000/api/v2.0/get-event-photo', json=x)
        if response.status_code == 200:
            image_name = str(id_event)
            extension = (response.headers['Content-Disposition'].split('.'))[-1]
            image_name += '.' + extension
            print(os.path.abspath('qr_site/static/img_background_event/'))
            img = open(os.path.abspath('qr_site/static/img_background_event/')+"/"+image_name, 'wb')
            img.write(response.content)
            img.close()
            # print(image_name)
        else:
            image_name = "anonimus_image.jpg"
            # print(image_name)

        id_path_img[str(id_event)] = '/static/img_background_event/' + image_name
        # print(response.content)
        # print(id_path_img)
        # print(url_for('static', filename=id_path_img[str(id_event)] ))
    return id_path_img


def get_current_user():
    return requests.get('http://80.78.245.132:5000/api/v2.0/get-current-user', cookies=request.cookies)