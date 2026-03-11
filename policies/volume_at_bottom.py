# policies/volume_at_bottom.py
from .base import BasePolicy

class Policy(BasePolicy):
    """
    底部放量策略：股价处于低位（接近60日低点）且成交量放大
    参数可在 config.yaml 的 policy_params 中设置：
        lookback: 回看周期（默认60，用于计算低点和高点）
        volume_lookback: 均量周期（默认20）
        volume_threshold: 量比阈值（默认2.0，即成交量超过均量倍数）
        low_distance: 股价距离60日低点的最大幅度（默认0.2，即20%以内）
        high_distance: 股价距离60日高点的最小幅度（可选，默认为None，不限制）
    """
    def get_expressions(self):
        lookback = self.params.get('lookback', 60)
        vol_lookback = self.params.get('volume_lookback', 20)
        return [
            "$close",
            "$volume",
            f"Min($low, {lookback})",
            f"Max($high, {lookback})",
            f"Mean($volume, {vol_lookback})",
            "$factor"
        ]

    def get_condition(self, df):
        lookback = self.params.get('lookback', 60)
        vol_lookback = self.params.get('volume_lookback', 20)
        volume_threshold = self.params.get('volume_threshold', 2.0)
        low_distance = self.params.get('low_distance', 0.2)
        high_distance = self.params.get('high_distance', None)

        low_min = df[f"Min($low, {lookback})"]
        high_max = df[f"Max($high, {lookback})"]
        close = df["$close"]
        volume = df["$volume"]
        vol_ma = df[f"Mean($volume, {vol_lookback})"]

        # 距离60日低点的涨幅
        dist_from_low = (close - low_min) / (low_min + 1e-10)
        # 量比
        vol_ratio = volume / (vol_ma + 1e-10)

        # 条件：股价在低点附近（涨幅小于 low_distance）且放量
        cond = (dist_from_low < low_distance) & (vol_ratio > volume_threshold)

        # 如果 high_distance 指定，则还要满足距离高点较远（避免追高）
        if high_distance is not None:
            dist_from_high = (high_max - close) / (close + 1e-10)
            cond = cond & (dist_from_high > high_distance)

        return cond

    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "Volume At Bottom"        