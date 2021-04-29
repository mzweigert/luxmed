from datetime import datetime
from time import sleep

from logger import *
from enum import Enum
from typing import Optional, Tuple, Any, Collection

from db.visits import VisitToBook
from api.luxmed import LuxMed
from api.luxmed.visits import VisitHours


class MedicalInsuranceType(Enum):
    LuxMed = 1


class MedicalInsuranceApi:
    def __init__(self, user_name: str, password: str, medical_insurance_type: MedicalInsuranceType):
        super().__init__()

        if medical_insurance_type == MedicalInsuranceType.LuxMed:
            self._api = LuxMed(user_name=user_name, password=password)
        else:
            raise Exception("Couldn't initialize api for medical insurance")

    def get_cities(self) -> dict:
        return self._api.cities()

    def get_clinics(self, city_id) -> dict:
        return self._api.clinics(city_id)

    def get_all_services(self, _city_id, _clinic_ids=None):
        services = self.__get_services(_city_id, _clinic_ids)
        referrals_services = self._api.referrals.services()
        return {**services, **referrals_services}

    def get_grouped_services(self, _city_id, _clinic_ids=None) -> dict:
        services = self.__get_services(_city_id, _clinic_ids)
        referrals_services = self._api.referrals.services_with_referral_ids()
        return {
            'services': services,
            'referral_services': referrals_services
        }

    def __get_services(self, _city_id, _clinic_ids=None) -> dict:
        _services = dict()
        if not _clinic_ids:
            _services = self._api.services(_city_id)
        else:
            for clinic_id in _clinic_ids:
                services_part = self._api.services(_city_id, clinic_id)
                _services.update(services_part)
        return _services

    def get_doctors(self, _city_id, _service_id, referral_id=None, _clinic_ids=None):
        _doctors = dict()
        if not _clinic_ids:
            _doctors = self._api.doctors(_city_id, _service_id, referral_id)
        else:
            for clinic_id in _clinic_ids:
                doctor_part = self._api.doctors(_city_id, _service_id, referral_id, clinic_id)
                _doctors.update(doctor_part)
        return _doctors

    def is_visit_already_reserved(self, _service_id):
        reserved_visits = self._api.visits.reserved()
        return any(reserved['Service']['Id'] == _service_id for reserved in reserved_visits['ReservedVisits'])

    def book_a_visit(self, visit: VisitToBook) -> Tuple[Optional[Any], VisitToBook]:
        time_from = datetime.strptime(visit.time_from, "%H:%M").time()
        time_to = datetime.strptime(visit.time_to, "%H:%M").time()

        details = None
        period = MedicalInsuranceApi.__get_hours_from_period(time_from, time_to)
        for visits in self.__find_available_visits(visit, period):
            sleep(2)
            details, wrong_clinic = self.__try_book_a_visit(time_from, time_to, visits, visit.referral_id)
            if wrong_clinic and wrong_clinic in visit.clinic_ids:
                visit.clinic_ids.remove(wrong_clinic)
            elif details:
                break
            sleep(2)

        return visit, details

    def __find_available_visits(self, visit, period):
        lang_id = self.__find_lang_id()
        payer = next(iter(self._api.payers(visit.city_id, visit.service_id)))['Id']
        sleep(2)
        for hours in period:
            if not visit.clinic_ids and not visit.doctor_ids:
                yield self._api.visits.find(visit.city_id, visit.service_id, lang_id, payer, referral_id=visit.referral_id,
                                            hours=hours, from_date=visit.date_from, to_date=visit.date_to)
            elif not visit.doctor_ids:
                for clinic_id in visit.clinic_ids:
                    yield self._api.visits.find(visit.city_id, visit.service_id, lang_id, payer, referral_id=visit.referral_id,
                                                clinic_id=clinic_id, hours=hours, from_date=visit.date_from, to_date=visit.date_to)
            elif not visit.clinic_ids:
                for doctor_id in visit.doctor_ids:
                    yield self._api.visits.find(visit.city_id, visit.service_id, lang_id, payer, doctor_id=doctor_id,
                                                referral_id=visit.referral_id,hours=hours, from_date=visit.date_from,
                                                to_date=visit.date_to)
            else:
                for clinic_id in visit.clinic_ids:
                    _available_doctors = set(self._api.doctors(visit.city_id, visit.service_id, clinic_id).keys())
                    _available_doctors = _available_doctors.intersection(visit.doctor_ids)
                    sleep(2)
                    for doctor_id in _available_doctors:
                        yield self._api.visits.find(visit.city_id, visit.service_id, lang_id, payer, clinic_id, doctor_id,
                                                    referral_id=visit.referral_id,hours=hours,
                                                    from_date=visit.date_from, to_date=visit.date_to)

    def __find_lang_id(self):
        for _id, lang in self._api.languages().items():
            if lang == 'polish':
                return _id
        return None

    @classmethod
    def __get_hours_from_period(cls, time_from: datetime.time, time_to: datetime.time) -> Collection[VisitHours]:
        if time_from.hour < 10 and time_to.hour > 17:
            return [VisitHours.ALL]

        hours = list()
        if time_from.hour < 10:
            hours.append(VisitHours.BEFORE_10)
        elif time_from.hour >= 10 and time_to.hour <= 17 and time_to.minute == 0:
            return [VisitHours.BETWEEN_10_TO_17]
        elif time_from.hour > 17:
            return [VisitHours.PAST_17]

        if 10 <= time_to.hour <= 17 and time_to.minute == 0:
            hours.append(VisitHours.BETWEEN_10_TO_17)
        else:
            hours.append(VisitHours.BETWEEN_10_TO_17)
            hours.append(VisitHours.PAST_17)

        return hours

    def __try_book_a_visit(self, time_from: datetime.time, time_to: datetime.time, visits, referral_id):
        wrong_clinic = None
        for visit in visits:
            if not visit['PayerDetailsList']:
                wrong_clinic = visit['Clinic']['Id']
                continue
            start_time = datetime.fromisoformat(visit['VisitDate']['StartDateTime']).replace(tzinfo=None).time()
            if time_from <= start_time <= time_to:
                logger.debug("Visit for user: {0} found!".format(self._api.user()['UserName']))
                logger.debug(visit)
                details = self._api.visits.reserve(clinic_id=visit['Clinic']['Id'], doctor_id=visit['Doctor']['Id'],
                                                   room_id=visit['RoomId'],
                                                   referral_id=referral_id,
                                                   service_id=visit['ServiceId'],
                                                   start_date_time=visit['VisitDate']['StartDateTime'],
                                                   is_additional=visit['IsAdditional'],
                                                   referral_required_by_service=visit['ReferralRequiredByService'],
                                                   payer_data=visit['PayerDetailsList'][0])
                logger.debug(details)
                return details, None
        return None, wrong_clinic

    def get_user_info(self):
        return self._api.user()
