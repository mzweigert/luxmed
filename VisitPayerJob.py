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

    scheduler.add_job(action, trigger='interval', minutes=15)
    atexit.register(lambda: scheduler.shutdown())
    print("Scheduler initialized.")


def action():
    visits = DBManager.get_all_visits()
    if not visits:
        print("No visits found")
        return
    for email, password in auth_data:
        if email not in visits:
            continue
        api = MedicalInsuranceApi(email, password, MedicalInsuranceType.LuxMed)
        for visit_to_book in visits[email]:
            print("I am trying book a visit with service_id = {0} for user = {1}".format(visit_to_book.service_id, email))
            visit_to_book, details = api.book_a_visit(visit_to_book)
            if details:
                print("Visit has been booked.")
                DBManager.remove_visit(visit_to_book.db_record_id)
            else:
                print("Couldn't find visit at this moment.")
