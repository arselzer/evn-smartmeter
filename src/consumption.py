from dataclasses import dataclass
from datetime import datetime, date


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
