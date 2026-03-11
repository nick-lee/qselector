# core/date_utils.py
import logging
import pandas as pd
from qlib.data import D

logger = logging.getLogger(__name__)

def get_calendar():
    """获取 Qlib 的交易日历（所有交易日）"""
    try:
        cal = D.calendar()
        if cal is None or len(cal) == 0:
            raise ValueError("Empty calendar")
        # 转换为 pandas DatetimeIndex 以确保类型一致
        return pd.DatetimeIndex(cal)
    except Exception as e:
        logger.error(f"Failed to get calendar: {e}")
        return None

def get_latest_data_date():
    """返回数据库中最新交易日（字符串 YYYY-MM-DD）"""
    cal = get_calendar()
    if cal is not None:
        return cal[-1].strftime('%Y-%m-%d')
    return None

def get_earliest_data_date():
    """返回数据库中最早交易日"""
    cal = get_calendar()
    if cal is not None:
        return cal[0].strftime('%Y-%m-%d')
    return None

def validate_date(requested_date):
    """
    验证请求日期是否为交易日，并返回可用的交易日。
    如果请求日期是交易日，则返回该日期；否则返回前一个交易日（若存在）。
    同时发出警告信息。
    """
    cal = get_calendar()
    if cal is None:
        logger.warning("Calendar unavailable, using requested date as-is.")
        return requested_date

    # 将请求日期转换为 Timestamp
    req = pd.Timestamp(requested_date)

    if req in cal:
        return req.strftime('%Y-%m-%d')
    else:
        # 找到小于等于请求日期的最后一个交易日
        valid_dates = cal[cal <= req]
        if len(valid_dates) == 0:
            logger.warning(f"Requested date {requested_date} is before earliest data date {cal[0].strftime('%Y-%m-%d')}. Using earliest date.")
            return cal[0].strftime('%Y-%m-%d')
        else:
            prev = valid_dates[-1]
            logger.warning(f"Requested date {requested_date} is not a trading day. Using previous trading day {prev.strftime('%Y-%m-%d')}.")
            return prev.strftime('%Y-%m-%d')

def check_data_freshness(requested_date):
    """
    检查请求日期相对于数据库最新日期的时效性，发出警告。
    """
    latest = get_latest_data_date()
    if latest is None:
        return
    if requested_date > latest:
        logger.warning(f"Requested date {requested_date} is later than latest data date {latest}. Data may be outdated.")
    elif requested_date < get_earliest_data_date():
        logger.warning(f"Requested date {requested_date} is earlier than earliest data date {get_earliest_data_date()}.")