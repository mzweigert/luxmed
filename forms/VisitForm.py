from wtforms import Form, StringField, validators, SelectField, SelectMultipleField, HiddenField


class VisitForm(Form):
    city_id = SelectField('Miasto', [validators.DataRequired()], render_kw={"data-live-search": "true"},
                          choices=[(None, '')], default=None, id="cities", coerce=int)
    clinic_ids = SelectMultipleField('Placówka', [validators.DataRequired()], render_kw={"data-live-search": "true"},
                                     choices=[], default=None, id="clinics", coerce=int)
    service_id = SelectField('Usługa', [validators.DataRequired()], render_kw={"data-live-search": "true"}, choices=[],
                             default=None, id="services", coerce=int)
    referral_id = HiddenField('Skierowanie', default=None, id="referral_id")
    doctor_ids = SelectMultipleField("Lekarz", [validators.DataRequired()], render_kw={"data-live-search": "true"},
                                     choices=[], default=None, id="doctors", coerce=int)
    time_from = StringField('Time from', [validators.DataRequired()], id="time-from")
    time_to = StringField('Time to', [validators.DataRequired()], id="time-to")
    date_from = StringField('Date from', [validators.DataRequired()], id="date-from")
    date_to = StringField('Date to', [validators.DataRequired()], id="date-to")
