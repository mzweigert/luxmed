from wtforms import Form, StringField, validators, SelectField, SelectMultipleField

from luxmed.visits import VisitHours

HOURS_CHOICES = [
    (str(VisitHours.ALL.value), "Wszystkie"),
    (str(VisitHours.BEFORE_10.value), "Przed 10"),
    (str(VisitHours.BETWEEN_10_TO_17.value), "Między 10 a 17"),
    (str(VisitHours.PAST_17.value), "Po 17")
]


class VisitForm(Form):
    city_id = SelectField('Miasto', [validators.DataRequired()], render_kw={"data-live-search": "true"},
                          choices=[(None, '')], default=None, id="cities", coerce=int)
    clinic_ids = SelectMultipleField('Placówka', [validators.DataRequired()], render_kw={"data-live-search": "true"},
                                     choices=[], default=None, id="clinics", coerce=int)
    service_id = SelectField('Usługa', [validators.DataRequired()], render_kw={"data-live-search": "true"}, choices=[],
                             default=None, id="services", coerce=int)
    hours = SelectField('Godziny', [validators.DataRequired()], choices=HOURS_CHOICES, coerce=str, default=None)
    date_from = StringField('Date from', [validators.DataRequired()], id="date-from")
    date_to = StringField('Date to', [validators.DataRequired()], id="date-to")
