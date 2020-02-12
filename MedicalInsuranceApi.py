from enum import Enum

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

    def book_a_visit(self, form) -> dict:
        data = MedicalInsuranceApi.VisitData(form)
        lang = next(iter(self._api.languages()))
        payer = next(iter(self._api.payers(data.city_id, data.service_id)))['Id']
        if not data.clinic_ids:
            visits = self._api.visits.find(data.city_id, data.service_id, lang, payer, hours=data.hours)
            return self.__try_book_a_visit(visits)
        else:
            for clinic_id in data.clinic_ids:
                visits_part = self._api.visits.find(data.city_id, data.service_id, lang, payer, clinic_id,
                                                    hours=data.hours)
                details = self.__try_book_a_visit(visits_part)
                if details:
                    return details

    def __try_book_a_visit(self, visits):
        for visit in visits:
            details = self._api.visits.reserve(clinic_id=visit['Clinic']['Id'], doctor_id=visit['Doctor']['Id'],
                                               room_id=visit['RoomId'],
                                               service_id=visit['ServiceId'],
                                               start_date_time=visit['VisitDate']['StartDateTime'],
                                               is_additional=visit['IsAdditional'],
                                               referral_required_by_service=visit['ReferralRequiredByService'],
                                               payer_data=visit['PayerDetailsList'][0])
            return details
        return None

    def get_user_info(self):
        return self._api.user()

    class VisitData(object):
        def __init__(self, dictionary: dict):
            for k in dictionary:
                if k == 'hours':
                    hours = VisitHours(int(dictionary[k]))
                    setattr(self, k, hours)
                elif k == 'clinic_ids' and dictionary[k][0] < 0:
                    setattr(self, k, None)
                else:
                    setattr(self, k, dictionary[k])

