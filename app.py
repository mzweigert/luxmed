# coding=utf-8
from MedicalInsuranceApi import MedicalInsuranceApi, MedicalInsuranceType
from VisitForm import VisitForm
from flask import Flask, request, render_template, jsonify

app = Flask(__name__, static_url_path='/static')

api = MedicalInsuranceApi()


@app.route('/', methods=['GET', 'POST'])
def home():
    _cities = api.get_cities().items()
    form = VisitForm()

    if request.method == 'POST':
        form = VisitForm(request.form)
        form.city_id.choices = _cities
        _clinics = api.get_clinics(form.city_id.data)
        _clinics[-1] = ''
        form.clinic_ids.choices = _clinics.items()
        _clinic_ids = form.clinic_ids.data
        if _clinic_ids[0] == -1:
            form.service_id.choices = api.get_services(form.city_id.data).items()
        else:
            form.service_id.choices = api.get_services(form.city_id.data, _clinic_ids).items()
        if form.validate():
            visit = api.book_a_visit(form.data)
            if not visit:
                return "Couldn't find visit at this moment"
            return visit

    form.city_id.choices = _cities

    return render_template('index.html', form=form)


@app.route("/clinics/<city_id>")
def clinics(city_id):
    _clinics = api.get_clinics(city_id)
    return jsonify(_clinics)


@app.route("/services", methods=['POST'])
def services():
    _clinic_ids = request.form.getlist('clinic_ids[]')
    _city_id = request.form.get('city_id')
    _services = api.get_services(_city_id, _clinic_ids)

    return jsonify(_services)


if __name__ == '__main__':
    app.run()
