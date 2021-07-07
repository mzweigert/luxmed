from datetime import datetime
from itertools import chain
from typing import Dict
from typing import Iterator

from api.luxmed.transformers import map_id_name
from api.luxmed.transport import LuxMedTransport
from api.luxmed.urls import REFERRALS_URL


class LuxMedReferrals:
    def __init__(self, transport: LuxMedTransport):
        self._transport = transport

    def results(self) -> Iterator[Dict]:
        """Yields referrals results between the given dates.
        """

        referrals = self._transport.get(REFERRALS_URL)
        for result in chain(
                referrals['UnplannedReferrals']['ExpiringSoonReferrals']['Referrals'],
                referrals['UnplannedReferrals']['RemainingReferrals']['Referrals'],
                referrals['PlannedReferrals']['Referrals']):
            valid_to = datetime.fromisoformat(result['ValidTo']['DateTime'])
            if valid_to >= datetime.now(tz=valid_to.tzinfo):
                yield result
            else:
                continue

    def services(self):
        results = self.results()
        referrals_services = list()
        for result in results:
            referrals_services.append(result['Service'])

        return map_id_name(referrals_services)

    def services_with_referral_ids(self) -> Dict[int, object]:
        results = self.results()
        referrals_services = dict()
        for result in results:
            referrals_services[result['Service']['Id']] = {'Name': result['Service']['Name'],
                                                           'ReferralId': result['ReferralId']}

        return referrals_services
