# coding=utf-8
from datetime import timedelta

from flask import Flask, request, render_template, jsonify, url_for, session
from flask_login import login_required, LoginManager, login_user
from werkzeug.utils import redirect
from expiringdict import ExpiringDict

from forms.LoginForm import LoginForm
from MedicalInsuranceApi import MedicalInsuranceApi, MedicalInsuranceType
from UserClass import UserClass
from forms.VisitForm import VisitForm
from luxmed.errors import LuxMedError

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'secret_key_ZXC235sdf'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

cache = ExpiringDict(max_len=100, max_age_seconds=60 * 60)


@login_manager.user_loader
def load_user(user_id):
    cache.get(user_id)


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session:
        form = LoginForm()
        return render_template('index.html', form=form)

    _cities = cache[session['user_id'] + '-api'].get_cities().items()
    form = VisitForm()

    if request.method == 'POST':
        form = VisitForm(request.form)
        form.city_id.choices = _cities
        _clinics = cache[session['user_id'] + '-api'].get_clinics(form.city_id.data)
        _clinics[-1] = ''
        form.clinic_ids.choices = _clinics.items()
        _clinic_ids = form.clinic_ids.data
        if _clinic_ids[0] == -1:
            form.service_id.choices = cache[session['user_id'] + '-api'].get_services(form.city_id.data).items()
        else:
            form.service_id.choices = cache[session['user_id'] + '-api'].get_services(form.city_id.data, _clinic_ids).items()
        if form.validate():
            visit = cache[session['user_id'] + '-api'].book_a_visit(form.data)
            if not visit:
                return "Couldn't find visit at this moment"
            return visit

    form.city_id.choices = _cities

    return render_template('index.html', form=form)


@app.route("/clinics/<city_id>")
@login_required
def clinics(city_id):
    _clinics = cache[session['user_id'] + '-api'].get_clinics(city_id)
    return jsonify(_clinics)


@app.route("/services", methods=['POST'])
@login_required
def services():
    _clinic_ids = request.form.getlist('clinic_ids[]')
    _city_id = request.form.get('city_id')
    _services = cache[session['user_id'] + '-api'].get_services(_city_id, _clinic_ids)

    return jsonify(_services)


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():

        try:
            api = MedicalInsuranceApi(form.email.data, form.password.data, MedicalInsuranceType.LuxMed)
            user = api.get_user_info()
            user = UserClass(form.email.data, user["AccountId"])
            cache[user.id] = user
            cache[user.id + '-api'] = api
            session['logged_in'] = True
            login_user(user, remember=form.remember_me.data)
        except LuxMedError:
            return redirect(url_for('index'))

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
    login = LoginManager(app)
