from datetime import datetime, timedelta
from statistics.constants import CycleConstant

from dateutil.relativedelta import relativedelta


def get_date_ranges(cycle, num_cycle, start_date, end_date):
    if not end_date:
        end_date = datetime.now()

    date_ranges = []

    if cycle == CycleConstant.DAY:
        if num_cycle:
            for i in range(num_cycle):
                date = datetime(
                    end_date.year, end_date.month, end_date.day
                ) - timedelta(days=i)
                date_ranges.append(date)
        else:
            while len(date_ranges) < 100:
                date = datetime(
                    end_date.year, end_date.month, end_date.day
                ) - timedelta(days=len(date_ranges))
                date_ranges.append(date)
                if start_date and date.date() < start_date:
                    break

    elif cycle == CycleConstant.WEEK:
        date = datetime(
            end_date.year, end_date.month, end_date.day - end_date.weekday()
        )
        if num_cycle:
            for i in range(num_cycle):
                date_ranges.append(date - timedelta(weeks=i))
        else:
            while len(date_ranges) < 100:
                date_ranges.append(date - timedelta(weeks=len(date_ranges)))
                if (
                    start_date
                    and (date - timedelta(weeks=len(date_ranges))).date() < start_date
                ):
                    break
    elif cycle == CycleConstant.MONTH:
        date = datetime(end_date.year, end_date.month, 1)
        if num_cycle:
            for i in range(num_cycle):
                date_ranges.append(date - relativedelta(months=i))
        else:
            while len(date_ranges) < 100:
                date_ranges.append(date - relativedelta(months=len(date_ranges)))
                if start_date and date_ranges[-1].date() < start_date:
                    break
    elif cycle == CycleConstant.QUARTER:
        date = datetime(end_date.year, end_date.month - (end_date.month - 1) % 3, 1)
        if num_cycle:
            for i in range(num_cycle):
                date_ranges.append(date - relativedelta(months=3 * i))
        else:
            while len(date_ranges) < 100:
                date_ranges.append(date - relativedelta(months=3 * len(date_ranges)))
                if start_date and date_ranges[-1].date() < start_date:
                    break

    elif cycle == CycleConstant.YEAR:
        date = datetime(end_date.year, 1, 1)
        if num_cycle:
            for i in range(num_cycle):
                date_ranges.append(date - relativedelta(years=i))
        else:
            while len(date_ranges) < 100:
                date_ranges.append(date - relativedelta(years=len(date_ranges)))
                if start_date and date_ranges[-1].date() < start_date:
                    break

    return [end_date] + date_ranges
