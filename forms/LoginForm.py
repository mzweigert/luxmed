from wtforms import PasswordField, StringField, BooleanField, SubmitField, SelectField, Form
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email

from MedicalInsuranceApi import MedicalInsuranceType

MEDICAL_INS_TYPES = [
    (MedicalInsuranceType.LuxMed.value, "LuxMed")
]


class LoginForm(Form):
    email = EmailField('Login', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    medical_type = SelectField('Opieka medyczna', validators=[DataRequired()], choices=MEDICAL_INS_TYPES,
                               default=MedicalInsuranceType.LuxMed.value, coerce=int)
    remember_me = BooleanField('Nie wylogowywuj mnie')
    submit = SubmitField('Zaloguj')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
