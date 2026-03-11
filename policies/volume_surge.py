# policies/volume_surge.py
from .base import BasePolicy

class Policy(BasePolicy):
    """
    成交量异动策略：当日成交量大于20日均量的指定倍数
    参数可在 config.yaml 的 policy_params 中设置：
        lookback: 均量计算周期（默认20）
        threshold: 倍数阈值（默认2.0，即成交量超过20日均量的2倍）
    """
    def get_expressions(self):
        lookback = self.params.get('lookback', 20)
        return [
            "$close",
            "$volume",
            f"Mean($volume, {lookback})",
            "$factor"
        ]

    def get_condition(self, df):
        lookback = self.params.get('lookback', 20)
        threshold = self.params.get('threshold', 2.0)
        volume = df["$volume"]
        vol_ma = df[f"Mean($volume, {lookback})"]
        # 避免除零
        ratio = volume / (vol_ma + 1e-10)
        return ratio > threshold

    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "Volume Surge"        