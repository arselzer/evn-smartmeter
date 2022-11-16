import requests

API_BASE = 'https://smartmeter.netz-noe.at'
API_LOGIN = '/orchestration/Authentication/Login'
API_BASIC_INFO = '/orchestration/User/GetBasicInfo'
API_GET_ACCOUNTS = '/orchestration/User/GetAccountIdByBussinespartnerId'
API_GET_METERING_POINTS = '/orchestration/User/GetMeteringPointByAccountId'
API_GET_CONSUMPTION_MONTH = '/orchestration/ConsumptionRecord/Month'

# TODO unused endpoints as of now
API_EXTEND_SESSION = '/orchestration/Authentication/ExtendSessionLifetime'


class Smartmeter:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookies = None
        self.session = requests.session()
        self.session.hooks['response'].append(self.reauthenticate)
        self.authenticate()

    def reauthenticate(self, res, *args, **kwargs):
        if res.status_code == requests.codes.unauthorized:
            print('Re-authenticating')
            self.authenticate()

            req = res.request
            print('Resending request', req.method, req.url, req.headers)

            return self.session.send(res.request)

    def authenticate(self):
        auth_payload = {
            'user': self.username,
            'pwd': self.password
        }
        response = self.session.post(API_BASE + API_LOGIN, json=auth_payload)
        if response.status_code != 200:
            raise SmartmeterAuthError(response.text)
        # TODO: determine when the session has expired, whether it is renewed by
        #  API calls and renew or extend it if needed

    def get_basic_info(self):
        response = self.session.get(API_BASE + API_BASIC_INFO)
        if response.status_code == 200:
            return response.json()
        else:
            raise SmartmeterError

    def get_accounts(self):
        response = self.session.get(API_BASE + API_GET_ACCOUNTS)
        if response.status_code == 200:
            return response.json()
        else:
            raise SmartmeterError

    def get_metering_points_for_account(self, account_id):
        response = self.session.get(API_BASE + API_GET_METERING_POINTS, params={'accountId': account_id})
        if response.status_code == 200:
            return response.json()
        else:
            raise SmartmeterError

    def get_all_metering_points(self):
        accounts = [a['accountId'] for a in self.get_accounts()]
        metering_points = []
        for account_id in accounts:
            metering_points = metering_points + self.get_metering_points_for_account(account_id)
        return metering_points

    def get_consumption_month(self, meter_id, year, month):
        response = self.session.get(API_BASE + API_GET_CONSUMPTION_MONTH,
                                    params={'meterId': meter_id, 'year': year, 'month': month})
        if response.status_code == 200:
            return response.json()
        else:
            raise SmartmeterError

class SmartmeterError(Exception):
    pass


class SmartmeterAuthError(SmartmeterError):
    pass
