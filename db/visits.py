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


class VisitToBook(object):
    def __init__(self, _city_id: int, _clinic_ids: [], _service_id: int,
                 _date_from: datetime.date, _date_to: datetime.date,
                 _time_from: str, _time_to: str,
                 user: str):
        self.city_id = _city_id
        self.clinic_ids = _clinic_ids
        self.service_id = _service_id
        self.date_from = try_parse_date(_date_from)
        self.date_to = try_parse_date(_date_to)
        self.time_from = _time_from
        self.time_to = _time_to
        self.user = user

    @classmethod
    def init_from(cls, data: dict):
        if data['clinic_ids'] and data['clinic_ids'][0] < 0:
            data['clinic_ids'] = None

        if 'user' not in data:
            data['user'] = None

        return VisitToBook(data['city_id'], data['clinic_ids'], data['service_id'],
                           data['date_from'], data['date_to'], data['time_from'], data['time_to'], data['user'])


class VisitToBookRecord(VisitToBook):
    def __init__(self, _city_id: int, _clinic_ids: [], _service_id: int,
                 _date_from: datetime.date, _date_to: datetime.date,
                 _time_from: str, _time_to: str,
                 user: str, db_record_id: str):
        super().__init__(_city_id, _clinic_ids, _service_id, _date_from, _date_to, _time_from, _time_to, user)
        self.db_record_id = db_record_id

    @classmethod
    def init_from_db(cls, data: dict, _rid):
        return VisitToBookRecord(data['city_id'], data['clinic_ids'], data['service_id'],
                                 data['date_from'], data['date_to'], data['time_from'], data['time_to'], data['user'],
                                 _rid)