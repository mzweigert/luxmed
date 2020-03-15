from configparser import ConfigParser

import pyorient

from db import UserClass, visits

cp = ConfigParser()
cp.read("auth.properties")
db_auth_data = next(iter(cp.items("db_auth")))


class DBConnection:
    __INITIALIZED = False

    def __init__(self):
        pass

    def __enter__(self):
        self.client = pyorient.OrientDB("localhost", 2424)
        self.session_id = self.client.connect(db_auth_data[0], db_auth_data[1])
        self.__init_db()
        return self.client

    def __exit__(self, type, value, traceback):
        self.client.close()

    def __init_db(self):
        if DBConnection.__INITIALIZED:
            return
        exists = self.client.db_exists("visits", pyorient.STORAGE_TYPE_PLOCAL)
        if not exists:
            self.client.db_create("visits", pyorient.DB_TYPE_GRAPH, pyorient.STORAGE_TYPE_PLOCAL)

        self.client.db_open("visits", "root", "password")
        user_exists = self.client.command(
            'SELECT FROM ( SELECT expand( classes ) FROM metadata:schema ) WHERE name = \'User\'')
        if not user_exists:
            self.client.command('create class User extends V')

        visit_to_book_exists = self.client.command(
            'SELECT FROM ( SELECT expand( classes ) FROM metadata:schema ) WHERE name = \'VisitToBook\'')
        if not visit_to_book_exists:
            self.client.command('create class VisitToBook extends V')

        DBConnection.__INITIALIZED = False


def visit_exists(visit: visits):
    with DBConnection() as client:
        if visit.clinic_ids:
            _visit_exists = client.query(str.format(
                'select from VisitToBook where city_id ={0} and clinic_ids = {1} and service_id = {2} '
                'and user = \'{3}\' and date_from >= \'{4}\' and date_to <= \'{5}\' '
                'and time_from >= \'{6}\' and time_to <= \'{7}\'',
                visit.city_id, visit.clinic_ids, visit.service_id, visit.user, visit.date_from, visit.date_to,
                visit.time_from, visit.time_to))
        else:
            _visit_exists = client.query(str.format(
                'select from VisitToBook where city_id ={0} and service_id = {1} '
                'and user = {2} and date_from >= {3} and date_to <= \'{4}\' ',
                'and time_from >= \'{5}\' and time_to <= \'{6}\'',
                visit.city_id, visit.service_id, visit.user, visit.date_from, visit.date_to, visit.time_from,
                visit.time_to))

        if _visit_exists:
            return True
        else:
            return False


def save_visit_to_book(visit: visits):
    with DBConnection() as client:
        record = {
            '@VisitToBook': visit.__dict__
        }
        client.record_create(-1, record)


def get_all_visits():
    with DBConnection() as client:
        _visits = client.query("select from VisitToBook")
        visits_to_book = dict()
        for v in _visits:
            visit = visits.VisitToBookRecord.init_from_db(v.oRecordData, v._rid)
            if visit.user not in visits_to_book:
                user_visits = list()
                user_visits.append(visit)
                visits_to_book.update({visit.user: user_visits})
            else:
                visits_to_book[visit.user].append(visit)

        return visits_to_book


def find_user(email: str):
    with DBConnection() as client:
        user = client.query(str.format('select from User where email =\'{0}\'', email))
        if not user:
            return None
        else:
            return UserClass.form_dictionary(user[0].oRecordData)


def find_user_by_id(_id):
    with DBConnection() as client:
        user = client.query(str.format('select from User where id =\'{0}\'', _id))
        if not user:
            return None
        else:
            return UserClass.form_dictionary(user[0].oRecordData)


def save_user(user: UserClass):
    with DBConnection() as client:
        user_exists = client.query(str.format('select from User where email =\'{0}\'', user.email))
        if not user_exists:
            record = {
                '@User': user.__dict__
            }
            client.record_create(-1, record)


def remove_visit(db_record_id):
    with DBConnection() as client:
        client.command(str.format('delete vertex from VisitToBook where @RID =\'{0}\'', db_record_id))
