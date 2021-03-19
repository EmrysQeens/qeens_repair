from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from model import *
from os import getenv
from urls import urls
from templates import templates
import string
import random
from jinja2 import Template
from re import match


db_url = getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)

cookies: dict = dict()


def generate_cookie(length: int) -> str:
    chars = string.ascii_lowercase + string.digits + string.punctuation
    return "".join(random.choice(chars) for char in range(length))


def create_user(email: str, username: str, password: str, is_super_user: bool = False, image: str = ""):
    user = User(username=username.lower(), email=email.lower(), password=password, is_super_user=is_super_user, image=image)
    db.session.add(user)
    db.session.commit()


def login(username: str, password: str) -> bool:
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        return redirect(url_for('index'), 302)
    response = make_response(redirect(url_for('home'), 302))
    cookie_value = generate_cookie(cookie_len)
    response.set_cookie('#user_token:id$', cookie_value)
    cookie = Cookie.query.get(cookie_value)
    if cookie is None:
        cookie = Cookie(cookie=cookie_value, user=user.id)
        db.session.add(cookie)
        db.session.commit()
    cookie.cookie = cookie_value
    cookie.user = user.id
    db.session.commit()
    return response


def validate(request_):
    cookie_val = request_.cookies.get('#user_token:id$')
    cookie = Cookie.query.get(cookie_val)
    if cookie is not None:
        return True
    return False


def authenticate(response, login_=True):
    cookie_val = request.cookies.get('#user_token:id$')
    cookie = Cookie.query.get(cookie_val)
    if cookie is None:
        if not login_:
            return response, False
        return redirect(url_for('index'), 302), False
    if cookie.cookie:
        return response, True
    return redirect(url_for('index'), 302), False


@app.route(urls['index'])
def index():
    response = make_response(redirect(url_for('home'), 302))
    auth: tuple = authenticate(response, False)
    if auth[1]:
        return auth[0]
    return render_template('layout.html', body=templates['login'], login=True, title='Login')


@app.route(urls['home'], methods=["POST", "GET"])
def home():
    if request.method == 'POST':
        username = request.form.get('user-id').lower()
        password = request.form.get('password')
        response = login(username, password)
        return response
    response = make_response(render_template('layout.html', title='Home'))
    return authenticate(response)[0]


@app.route(urls['event'], methods=["POST"])
def app_event():
    if request.method == 'POST' and validate(request):
        cookie_val = request.cookies.get('#user_token:id$')
        cookie = Cookie.query.get(cookie_val)
        user = User.query.get(cookie.user)
        event: str = request.form.get('event')

        def get(x):
            return request.form.get(x)

        if event == 'logout':
            return logout()
        elif event == "template":
            contexts = {
                'register': {'manufacturers': Manufacturer.query.all(), 'register': True},
                "search": {},
                'welcome': {'user': user, 'image': url_for('static', filename='img.jpeg'), 'none': None}
            }
            template: str = request.form.get('template')
            tmp = templates[template]
            rendered_tmp = Template(tmp['html']).render(contexts[template])
            response = make_response(jsonify({'html': rendered_tmp, 'js': tmp['js']}))
            return authenticate(response)[0]
        elif event == 'edit_save':
            cost, paid = int(get('cost')) if get('cost') != "" else 0, int(get('paid')) if get('paid') != "" else 0
            print(get('cost'))
            print(get('paid'))
            if paid > cost:
                return jsonify({'stat': 'amount_err'})
            id = request.form.get('id')
            repair = Repair.query.get(id)
            if repair is None:
                return jsonify({'stat': 'err'})
            customer = Customer.query.get(repair.customer)
            if get('imei') != "":
                imei = Imei.query.filter_by(imei=get('imei')).first()
                if imei is None:
                    imei = Imei(imei=get('imei'))
                    db.session.add(imei)
                    db.session.commit()
                    imei = imei
                if repair.imei != "":
                    print(repair.imei)
                    imei_ = Imei.query.get(repair.imei)
                    if get('imei') != imei_.imei:
                        repair.imei = imei.id
                    if len(imei_.repairs) == 0:
                        db.session.delete(imei_)
            else:
                repair.imei = ""
            customer_check = Customer.query.filter_by(mobile_number=get('mobile_number')).first()
            if customer_check is None:
                return jsonify({'stat': 'no_customer'})
            customer.first_name, customer.last_name = get('first_name').capitalize(), get('last_name').capitalize()
            customer.image = get('image')
            repair.manufacturer = Manufacturer.query.filter_by(name=get('manufacturer')).first().id
            repair.model, repair.device_pass, repair.fault, repair.battery_serial_no, = get('model').upper(), get(
                'device_pass'), get('fault'), get('battery_serial_no'),
            repair.accessories_collected = get('accessories_collected')
            repair.cost, repair.paid, repair.balance = cost, paid, cost-paid, cost-paid
            db.session.commit()
            return jsonify({'stat': 'ok'})
        elif event == 'register':
            cost, paid = int(get('cost')) if get('cost') != "" else 0, int(get('paid')) if get('paid') != "" else 0
            if paid > cost:
                return jsonify({'stat': 'amount_err'})
            first_name, last_name, image, mobile_number = get('first_name').capitalize(), \
                                                          get('last_name').capitalize(), \
                                                          get('image'), get('mobile_number')  # todo phone number.
            customer = Customer.query.filter_by(mobile_number=mobile_number).first()
            if customer is None:
                customer = Customer(first_name=first_name, last_name=last_name,
                                    image=image, mobile_number=mobile_number)
                db.session.add(customer)
                db.session.commit()
            else:
                if customer.first_name != first_name or customer.last_name != last_name:
                    return jsonify({'stat': 'mobile_err', 'name': f'{customer.first_name} {customer.last_name}'})
            customer.image = customer.image if get('image') == "" else get('image')
            manufacturer = Manufacturer.query.filter_by(name=get('manufacturer')).first()  # manufacturer
            if manufacturer is None:
                return jsonify({'stat': 'err_manufacturer'})
            imei = get('imei')  # imei
            if imei != "" and len(imei) == 15:
                imei_ = Imei.query.filter_by(imei=imei).first()
                if imei_ is None:
                    imei = Imei(imei=imei)
                    db.session.add(imei)
                    db.session.commit()
                else:
                    imei = imei_
            repair = Repair(  # repair
                manufacturer=manufacturer.id,
                model=get('model').upper(), device_pass=get('device_pass'), fault=get('fault'),
                battery_serial_no=get('battery_serial_no'), date_b=get('date_b'),
                accessories_collected=get('accessories_collected'), date_c="",
                registerer=user.id
            )
            repair.cost, repair.paid, repair.balance = (get('cost'), get('paid'),
                                                        int(get('cost')) - int(get('paid'))) if get('cost') and get(
                'paid') != "" else (0, 0, 0)
            repair.customer = customer.id
            customer.repairs.append(repair)
            manufacturer.repairs.append(repair)
            if get('imei') != "":
                imei.repairs.append(repair)
            db.session.add(repair)
            db.session.commit()
            return jsonify({'stat': 'ok'})
        elif event == 'manufacturer':
            manufacturer = request.form.get('manufacturer').capitalize()
            manufacturer_ = Manufacturer.query.filter_by(name=manufacturer).first()
            if manufacturer_ is None:
                manufacturer = Manufacturer(name=manufacturer)
                db.session.add(manufacturer)
                db.session.commit()
                return jsonify({'stat': True})
            return jsonify({'stat': False})
        elif event == 'search':
            query, pos = request.form.get('query'), int(request.form.get('pos'))
            if match(r'^(mobile:[0-9]{11}|imei:[0-9]{15})$', query) is None:
                return jsonify({'stat': 'err'})
            search_by = (Customer.query.filter_by(mobile_number=query[8:]).first(), True) if query.startswith(
                'mobile:') else (Imei.query.filter_by(imei=query[5:]).first(), False)
            model, bool_type = search_by
            if model is None:
                return jsonify({'stat': 'no_customer' if search_by[1] else 'no_imei'})
            repairs = model.repairs
            if len(repairs) <= pos or pos < 0:
                return jsonify({'stat': 'err'})
            repair = repairs[pos]
            if repair is None:
                return jsonify({'stat': 'no_repair_cus' if search_by[1] else 'no_repair_imei'})  # todo
            manufacturer = Manufacturer.query.get(repair.manufacturer)
            customer, imei = (model, Imei.query.get(repair.customer),) if bool_type else (
                Customer.query.get(repair.customer), model)
            context = {
                'customer': customer, 'manufacturer': manufacturer, 'repair': repair, 'len': len(repairs),
                'pos': pos, 'User': User, 'user': user,
                'image': url_for('static', filename='img.jpeg'), 'imei': imei
            }
            view = Template(templates['view']['html']).render(context)
            return jsonify({'stat': 'repair', 'html': view, 'js': templates['view']['js']})
        elif event == 'deliver':
            user = cookie.user
            repair = Repair.query.get(request.form.get('id'))
            if repair is None:
                return jsonify({'stat': 'err'})
            repair.date_c, repair.deliverer = [request.form.get('date_c'), user] if request.form.get(
                'checked') == 'true' else ["", ""]
            db.session.commit()
            return jsonify({'stat': True})
        elif event == 'edit':  # TODO
            repair = Repair.query.get(request.form.get('id'))
            if repair is None:
                return jsonify({'stat': False})
            customer = Customer.query.get(repair.customer)
            manufacturer = Manufacturer.query.get(repair.manufacturer)
            imei = Imei.query.get(repair.imei)
            context = {
                'manufacturer_': manufacturer, 'register': False,
                'customer': customer, 'imei': imei, 'repair': repair,
                'manufacturers': Manufacturer.query.all(), 'none': None,
                'mobile_number': f'0{customer.mobile_number}'
            }
            template = templates['register']
            html = Template(template['html']).render(context)
            return jsonify({'html': html, 'js': template['js'], 'stat': True})
        elif event == 'change_psw':
            old_psw, new_psw = request.form.get('psw_old'), request.form.get('psw_new')
            if user.password != old_psw:
                return jsonify({'stat': 'psw_error'})
            user.password = new_psw
            db.session.commit()
            return jsonify({'stat': 'psw_changed'})
        elif event == 'delete':
            id_ = request.form.get('id')
            repair = Repair.query.get(id_)
            if repair == None:
                return jsonify({'stat': 'no_rep'})
            if user.is_super_user:
                db.session.delete(repair)
                db.session.commit()
                return jsonify({'stat': 'ok'})
            return jsonify({'stat': 'no_permission'})
        elif event == 'sv_usr':
            action = request.form.get('action')
            data = {'action': action}
            username, email, image, password, su = get('username'), get('email'), get('image'), get(
                'password_user'), get('super_user')
            if action == 'user_edit':
                if user.password == password:
                    user.username, user.email, user.image = username, email, image
                    db.session.commit()
                    data['stat'] = "updated"
                    return jsonify(data)
                data['stat'] = "err"
                return jsonify(data)
            else:
                create_user(username=username, password=password, is_super_user=True if su == 'true' else False,
                            image=image, email=email)
                data['stat'] = 'created'
                return jsonify(data)
        elif event == 'user':
            id_ = request.form.get('id')
            context = {'user': user, 'new': True if id_ == 'user_new' else False}
            html = Template(templates['user']['html']).render(context)
            return jsonify({'html': html, 'js': templates['user']['js']})
        return jsonify({})


def logout():
    response = make_response(redirect(url_for('index'), 302))
    response.set_cookie('#user_token:id$', '', max_age=0)
    resp = authenticate(response)
    if resp[1]:
        db.session.delete(Cookie.query.get(request.cookies.get('#user_token:id$')))
        db.session.commit()
        return resp[0]
    return resp[0]


def err_404(e):
    return render_template('error.html', err=404)


def err_500(e):
    return render_template('error.html', err=500)


err_405 = lambda e: render_template('error.html', err=405)


if __name__ == '__main__':
    db.create_all(app=app, bind=None)
    app.register_error_handler(404, err_404)
    app.register_error_handler(500, err_500)
    app.register_error_handler(405, err_405)
    Flask.run(self=app, debug=True, port=5000)
