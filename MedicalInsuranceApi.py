from enum import Enum
from typing import Optional, Tuple, Any

from db.VisitToBook import VisitToBook
from luxmed import LuxMed
from luxmed.visits import VisitHours


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

    def get_services(self, _city_id, _clinic_ids=None) -> dict:
        _services = dict()
        if not _clinic_ids:
            _services = self._api.services(_city_id)
        else:
            for clinic_id in _clinic_ids:
                services_part = self._api.services(_city_id, clinic_id)
                _services.update(services_part)
        return _services

    def book_a_visit(self, visit: VisitToBook) -> Tuple[Optional[Any], VisitToBook]:
        lang_id = None
        for _id, lang in self._api.languages().items():
            if lang == 'polish':
                lang_id = _id
        payer = next(iter(self._api.payers(visit.city_id, visit.service_id)))['Id']
        details = None
        if not visit.clinic_ids:
            visits = self._api.visits.find(visit.city_id, visit.service_id, lang_id, payer, hours=VisitHours(visit.hours),
                                           from_date=visit.date_from, to_date=visit.date_to)
            details = self.__try_book_a_visit(visits)
        else:
            for clinic_id in visit.clinic_ids:
                visits_part = self._api.visits.find(visit.city_id, visit.service_id, lang_id, payer, clinic_id,
                                                    hours=VisitHours(visit.hours), from_date=visit.date_from,
                                                    to_date=visit.date_to)
                details, wrong_clinic = self.__try_book_a_visit(visits_part)
                if wrong_clinic:
                    visit.clinic_ids.remove(clinic_id)
                elif details:
                    break

        return visit, details

    def __try_book_a_visit(self, visits):
        wrong_clinic = False
        for visit in visits:
            if visit['PayerDetailsList']:
                details = self._api.visits.reserve(clinic_id=visit['Clinic']['Id'], doctor_id=visit['Doctor']['Id'],
                                                   room_id=visit['RoomId'],
                                                   service_id=visit['ServiceId'],
                                                   start_date_time=visit['VisitDate']['StartDateTime'],
                                                   is_additional=visit['IsAdditional'],
                                                   referral_required_by_service=visit['ReferralRequiredByService'],
                                                   payer_data=visit['PayerDetailsList'][0])
                wrong_clinic = False
                return details, wrong_clinic
            else:
                wrong_clinic = True
        return None, wrong_clinic

    def get_user_info(self):
        return self._api.user()
