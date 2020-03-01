import datetime

from luxmed.visits import VisitHours


def try_parse_date(_date):
    if type(_date) is datetime.datetime:
        return _date.date()
    elif type(_date) is datetime.date:
        return _date
    else:
        parsed_date = _date.split('.')
        return datetime.date(int(parsed_date[2]), int(parsed_date[1]), int(parsed_date[0]))


def init_from(data: dict, db_record_id=None):
    if data['clinic_ids'] and data['clinic_ids'][0] < 0:
        data['clinic_ids'] = None

    if isinstance(data['hours'], str):
        data['hours'] = int(data['hours'])

    if 'user' not in data:
        data['user'] = None

    if db_record_id:
        return VisitToBookRecord(data['city_id'], data['clinic_ids'], data['service_id'], data['hours'],
                                 data['date_from'], data['date_to'], data['user'], db_record_id)
    else:
        return VisitToBook(data['city_id'], data['clinic_ids'], data['service_id'], data['hours'], data['date_from'],
                           data['date_to'], data['user'])


class VisitToBook(object):
    def __init__(self, _city_id: int, _clinic_ids: [], _service_id: int,
                 _hours: int, _date_from: str, _date_to: str, user: str):
        self.city_id = _city_id
        self.clinic_ids = _clinic_ids
        self.service_id = _service_id
        self.hours = _hours
        self.date_from = try_parse_date(_date_from)
        self.date_to = try_parse_date(_date_to)
        self.user = user


class VisitToBookRecord(VisitToBook):
    def __init__(self, _city_id: int, _clinic_ids: [], _service_id: int, _hours: int, _date_from: str, _date_to: str,
                 user, db_record_id: str):
        super().__init__(_city_id, _clinic_ids, _service_id, _hours, _date_from, _date_to, user)
        self.db_record_id = db_record_id
