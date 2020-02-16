HOST = 'portalpacjenta.luxmed.pl'
BASE_URL = f'https://{HOST}'
BASE_API_URL = f'{BASE_URL}/PatientPortalMobileAPI/api'
TOKEN_URL = f'{BASE_API_URL}/token'
ACCOUNT_URL = f'{BASE_API_URL}/account'
EXAMINATION_RESULTS_URL = f'{BASE_API_URL}/medical-examinations-results'
USER_URL = f'{ACCOUNT_URL}/user'
USER_PERMISSIONS_URL = f'{USER_URL}/permissions'
VISITS_URL = f'{BASE_API_URL}/visits'
VISIT_RESERVE_TEMPORARY_URL = f'{VISITS_URL}/temporary-reservation'
VISIT_RESERVE_URL = f'{VISITS_URL}/reserved'
VISIT_TERMS_URL = f'{VISITS_URL}/available-terms'
VISIT_TERMS_RESERVATION_URL = f'{VISIT_TERMS_URL}/reservation-filter'
VISIT_TERMS_VALUATION_URL = f'{VISIT_TERMS_URL}/valuations'
REFERRALS_URL = f'{BASE_API_URL}/medical-referrals'
HISTORY_VISITS_URL = f'{VISITS_URL}/history'
RESERVED_VISITS_URL = f'{VISITS_URL}/reserved'
