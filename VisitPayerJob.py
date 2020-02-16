import atexit
from configparser import ConfigParser

from apscheduler.schedulers.background import BackgroundScheduler

from MedicalInsuranceApi import MedicalInsuranceApi, MedicalInsuranceType
from db import DBManager

cp = ConfigParser()
cp.read("auth.properties")
auth_data = cp.items("auth")


def init():
    scheduler = BackgroundScheduler()
    scheduler.start()

    scheduler.add_job(action, trigger='interval', minutes=30)
    atexit.register(lambda: scheduler.shutdown())


def action():
    visits = DBManager.get_all_visits()
    if not visits:
        return
    for email, password in auth_data:
        if email not in visits:
            continue
        api = MedicalInsuranceApi(email, password, MedicalInsuranceType.LuxMed)
        for visit_to_book in visits[email]:
            visit = api.book_a_visit(visit_to_book)
            if visit:
                DBManager.remove_visit(visit_to_book.db_record_id)