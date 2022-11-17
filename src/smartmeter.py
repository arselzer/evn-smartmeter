import requests
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta

API_BASE = 'https://smartmeter.netz-noe.at'
API_LOGIN = '/orchestration/Authentication/Login'
API_BASIC_INFO = '/orchestration/User/GetBasicInfo'
API_GET_ACCOUNTS = '/orchestration/User/GetAccountIdByBussinespartnerId'
API_GET_METERING_POINTS = '/orchestration/User/GetMeteringPointByAccountId'
API_GET_CONSUMPTION_YEAR = '/orchestration/ConsumptionRecord/Year'
API_GET_CONSUMPTION_MONTH = '/orchestration/ConsumptionRecord/Month'
API_GET_CONSUMPTION_DAY = '/orchestration/ConsumptionRecord/Day'

API_EXTEND_SESSION = '/orchestration/Authentication/ExtendSessionLifetime'


@dataclass
class Consumption:
    metered_value: float
    estimated_value: float
    grid_usage_leftover_values: float
    self_coverage_values: float
    joint_tenancy_proportion_values: float
    metered_peak_demand: float
    estimated_peak_demand: float


@dataclass
class QuarterHourlyConsumption(Consumption):
    start: datetime
    end: datetime


@dataclass
class DailyConsumption(Consumption):
    day: date


@dataclass
class MonthlyConsumption(Consumption):
    start: date


@dataclass
class YearlyConsumption(Consumption):
    year: str


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
            logging.info('Re-authenticating')
            self.authenticate()

            req = res.request
            logging.info('Resending request')

            cookie_str = ';'.join(['%s=%s' % (name, value) for (name, value) in dict(self.session.cookies).items()])
            req.headers['Cookie'] = cookie_str

            return self.session.send(res.request)

    def authenticate(self):
        auth_payload = {
            'user': self.username,
            'pwd': self.password
        }
        response = self.session.post(API_BASE + API_LOGIN, json=auth_payload)
        if response.status_code != 200:
            raise SmartmeterAuthError(response.text)

    def get_basic_info(self):
        response = self.session.get(API_BASE + API_BASIC_INFO)
        if response.status_code == 200:
            return response.json()
        else:
            raise SmartmeterError(response.text)

    def get_accounts(self):
        response = self.session.get(API_BASE + API_GET_ACCOUNTS)
        if response.status_code == 200:
            return response.json()
        else:
            raise SmartmeterError(response.text)

    def get_metering_points_for_account(self, account_id):
        response = self.session.get(API_BASE + API_GET_METERING_POINTS, params={'accountId': account_id})
        if response.status_code == 200:
            return response.json()
        else:
            raise SmartmeterError(response.text)

    def get_all_metering_points(self):
        accounts = [a['accountId'] for a in self.get_accounts()]
        metering_points = []
        for account_id in accounts:
            metering_points = metering_points + self.get_metering_points_for_account(account_id)
        return metering_points

    @staticmethod
    def _make_consumption_instance(api_result, i):
        metered_value = api_result['meteredValues'][i]
        estimated_value = api_result['estimatedValues'][i]
        grid_usage_leftover_value = api_result['gridUsageLeftoverValues'][i]
        self_coverage_value = api_result['selfCoverageValues'][i]
        joint_tenancy_proportion_value = api_result['jointTenancyProportionValues'][i]
        metered_peak_demand = api_result['meteredPeakDemands'][i]
        estimated_peak_demand = api_result['estimatedPeakDemands'][i]

        return Consumption(metered_value, estimated_value, grid_usage_leftover_value,
                           self_coverage_value, joint_tenancy_proportion_value,
                           metered_peak_demand, estimated_peak_demand)

    def get_consumption_year(self, meter_id, year):
        response = self.session.get(API_BASE + API_GET_CONSUMPTION_MONTH,
                                    params={'meterId': meter_id, 'year': year})
        if response.status_code == 200:
            result = []
            api_result = response.json()
            times = [datetime.fromisoformat(d) if d is not None else None for d in api_result['peakDemandTimes']]
            for i, t in enumerate(times):
                c = self._make_consumption_instance(api_result, i)

                result.append(MonthlyConsumption(c.metered_value, c.estimated_value, c.grid_usage_leftover_values,
                                                 c.self_coverage_values, c.joint_tenancy_proportion_values,
                                                 c.metered_peak_demand, c.estimated_peak_demand, t))
            return result
        else:
            raise SmartmeterError(response.text)

    def get_consumption_month(self, meter_id, year, month):
        response = self.session.get(API_BASE + API_GET_CONSUMPTION_MONTH,
                                    params={'meterId': meter_id, 'year': year, 'month': month})
        if response.status_code == 200:
            result = []
            api_result = response.json()
            times = [datetime.fromisoformat(d) if d is not None else None for d in api_result['peakDemandTimes']]
            for i, t in enumerate(times):
                c = self._make_consumption_instance(api_result, i)

                result.append(DailyConsumption(c.metered_value, c.estimated_value, c.grid_usage_leftover_values,
                                               c.self_coverage_values, c.joint_tenancy_proportion_values,
                                               c.metered_peak_demand, c.estimated_peak_demand, t))
            return result
        else:
            raise SmartmeterError(response.text)

    def get_consumption_day(self, meter_id, day: date):
        response = self.session.get(API_BASE + API_GET_CONSUMPTION_DAY,
                                    params={'meterId': meter_id, 'day': f'{day.year}-{day.month}-{day.day}'})
        if response.status_code == 200:
            result = []
            api_result = response.json()
            times = [datetime.fromisoformat(d) if d is not None else None for d in api_result['peakDemandTimes']]
            for i, t in enumerate(times):
                c = self._make_consumption_instance(api_result, i)
                time_start = t - timedelta(minutes=15)
                time_end = t

                result.append(QuarterHourlyConsumption(c.metered_value, c.estimated_value, c.grid_usage_leftover_values,
                                                       c.self_coverage_values, c.joint_tenancy_proportion_values,
                                                       c.metered_peak_demand, c.estimated_peak_demand,
                                                       time_start, time_end))
            return result
        else:
            raise SmartmeterError(response.text)


class SmartmeterError(Exception):
    pass


class SmartmeterAuthError(SmartmeterError):
    pass
