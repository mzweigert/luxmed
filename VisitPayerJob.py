from configparser import ConfigParser

from MedicalInsuranceApi import MedicalInsuranceApi, MedicalInsuranceType, logger
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
        for visit_to_book in visits[email]:
            logger.debug(
                "I am trying book a visit with service_id = {0} for user = {1}".format(visit_to_book.service_id, email))
            visit_to_book, details = api.book_a_visit(visit_to_book)
            if details:
                logger.debug("Visit has been booked.")
                DBManager.remove_visit(visit_to_book.db_record_id)
            else:
                logger.debug("Couldn't find visit at this moment.")


if __name__ == '__main__':
    logger.debug("Job run.")
    action()
