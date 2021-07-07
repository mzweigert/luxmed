from configparser import ConfigParser
from time import sleep

from api.MedicalInsuranceApi import MedicalInsuranceApi, MedicalInsuranceType, logger
from db import DBManager


cp = ConfigParser()
cp.read("auth.properties")
auth_data = cp.items("auth")


def action():
    visits = DBManager.get_all_visits()
    if not visits:
        logger.debug("No visits found")
        return
    for email, password in auth_data:
        if email not in visits:
            continue
        api = MedicalInsuranceApi(email, password, MedicalInsuranceType.LuxMed)
        sleep(2)
        booked_services_for_user = BookedServicesForUser(email)
        for visit_to_book in visits[email]:
            if visit_to_book.service_id in booked_services_for_user:
                logger.debug(
                    "Visit with service_id = {0} for user = {1} already booked".format(visit_to_book.service_id, email))
                DBManager.remove_visit(visit_to_book.db_record_id)
                continue

            logger.debug(
                "I am trying book a visit with service_id = {0} for user = {1}".format(visit_to_book.service_id, email))
            visit_to_book, details = api.book_a_visit(visit_to_book)
            if details:
                logger.debug("Visit has been booked.")
                booked_services_for_user.add(visit_to_book.service_id)
                DBManager.remove_visit(visit_to_book.db_record_id)
            else:
                logger.debug("Couldn't find visit at this moment.")
            logger.debug("Wait 5 seconds to try book next visit...")
            sleep(5)


class BookedServicesForUser(object):
    def __init__(self, _email: str):
        self.email = _email
        self.service_ids = set()

    def add(self, _service_id: int):
        self.service_ids.add(_service_id)

    def __contains__(self, item):
        return item in self.service_ids


if __name__ == '__main__':
    logger.debug("Job run.")
    action()
