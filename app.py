# coding=utf-8
from configparser import ConfigParser
from datetime import timedelta

from flask import Flask, request, render_template, jsonify, url_for, session
from flask_login import LoginManager, login_user, logout_user
from werkzeug.utils import redirect
from expiringdict import ExpiringDict

from db import DBManager, visits
from forms.LoginForm import LoginForm
from api.MedicalInsuranceApi import MedicalInsuranceApi, MedicalInsuranceType
from db.UserClass import UserClass
from forms.VisitForm import VisitForm
from api.luxmed.errors import LuxMedError

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'secret_key_ZXC235sdf'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

cache = ExpiringDict(max_len=100, max_age_seconds=60 * 60)

cp = ConfigParser()
cp.read("auth.properties")
auth_data = dict(cp.items("auth"))


@login_manager.user_loader
def load_user(user_id):
    cache.get(user_id)


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


@app.route('/', methods=['GET', 'POST'])
def index():
    if not get_user_id_from_session() or get_user_id_from_session() not in cache:
        logout_user()
        return redirect(url_for('login'))

    user_id = get_user_id_from_session()
    _cities = cache[user_id + '-api'].get_cities().items()
    form = VisitForm()
    if request.method == 'POST':
        form = VisitForm(request.form)
        form.city_id.choices = list(_cities)
        _clinics = cache[user_id + '-api'].get_clinics(form.city_id.data)
        _clinics[-1] = ''
        form.clinic_ids.choices = list(_clinics.items())
        _clinic_ids = form.clinic_ids.data
        if _clinic_ids[0] == -1:
            _services = cache[user_id + '-api'].get_all_services(form.city_id.data)
            _doctors = cache[user_id + '-api'].get_doctors(form.city_id.data, form.service_id.data)
        else:
            _services = cache[user_id + '-api'].get_all_services(form.city_id.data, _clinic_ids)
            _doctors = cache[user_id + '-api'].get_doctors(form.city_id.data, form.service_id.data, _clinic_ids)
        _doctors[-1] = ''
        form.service_id.choices = list(_services.items())
        form.doctor_ids.choices = list(_doctors.items())

        if form.validate():
            return handle_visit_request(form, user_id)

    form.city_id.choices = list(_cities)

    return render_template('index.html', form=form)


def handle_visit_request(form, user_id):
    data = visits.VisitToBook.init_from(form.data)
    data.user = cache[user_id].email
    exists = DBManager.visit_exists(data)
    reserved = cache[user_id + '-api'].is_visit_already_reserved(data.service_id)
    if reserved:
        return "Masz już zarezerowaną wizytę dla podanej usługi"
    elif exists:
        return "Wizyta z podanymi kryteriami została już zapisana do rezerwacji"
    else:
        data, details = cache[user_id + '-api'].book_a_visit(data)
        if not details:
            DBManager.save_visit_to_book(data)
            return "Nie zarezerowano wizyty w tym momencie, ale została ona zapisana do rezerwacji"
        return details


@app.route("/clinics/<city_id>")
def clinics(city_id):
    if not get_user_id_from_session():
        form = LoginForm()
        return render_template('index.html', form=form)

    _clinics = cache[get_user_id_from_session() + '-api'].get_clinics(city_id)
    return jsonify(_clinics)


@app.route("/services", methods=['POST'])
def services():
    if not get_user_id_from_session():
        form = LoginForm()
        return render_template('index.html', form=form)

    _clinic_ids = request.form.getlist('clinic_ids[]')
    _city_id = request.form.get('city_id')
    _services = cache[get_user_id_from_session() + '-api'].get_grouped_services(_city_id, _clinic_ids)

    return jsonify(_services)


@app.route("/doctors", methods=['POST'])
def doctors():
    if not get_user_id_from_session():
        form = LoginForm()
        return render_template('index.html', form=form)

    _clinic_ids = request.form.getlist('clinic_ids[]')
    _city_id = request.form.get('city_id')
    _service_id = request.form.get('service_id')
    _referral_id = request.form.get('referral_id')
    _doctors = cache[get_user_id_from_session() + '-api'].get_doctors(_city_id, _service_id, _referral_id, _clinic_ids)

    return jsonify(_doctors)


def get_user_id_from_session():
    if 'user_id' in session:
        return session['user_id']
    elif '_user_id' in session:
        return session['_user_id']
    return None


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if not get_user_id_from_session() or get_user_id_from_session() not in cache:
            form = LoginForm()
            return render_template('login.html', form=form)
        else:
            return redirect(url_for('index'))

    form = LoginForm(request.form)
    if not form.validate():
        return render_template('login.html', form=form, error_msg="Nieprawidłowe dane")

    try:
        user = DBManager.find_user(form.email.data)
        if not user:
            api = MedicalInsuranceApi(form.email.data, form.password.data, MedicalInsuranceType.LuxMed)
            user = api.get_user_info()
            user = UserClass(form.email.data, user["AccountId"])
            DBManager.save_user(user)
        elif user and auth_data[form.email.data] == form.password.data:
            api = MedicalInsuranceApi(form.email.data, form.password.data, MedicalInsuranceType.LuxMed)
        else:
            return render_template('login.html', form=form, error_msg="Nieprawidłowe hasło")

        cache[user.id] = user
        cache[user.id + '-api'] = api
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    except LuxMedError as e:
        if e.code == 2:
            error_msg = "Nieprawidłowy login lub hasło"
        else:
            error_msg = "System nie mógł zalogować do opieki medycznej, spróbuj ponownie."

    return render_template('login.html', form=form, error_msg=error_msg)


if __name__ == '__main__':
    app.run()
    login = LoginManager(app)
