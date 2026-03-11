# policies/williams_oversold.py
from .base import BasePolicy

class Policy(BasePolicy):
    """
    威廉指标（W%R）超卖策略：W%R < threshold（默认 -80）
    参数可在 config.yaml 的 policy_params 中设置：
        period: 计算周期（默认14）
        threshold: 超卖阈值（默认 -80，即低于-80为超卖）
    """
    def get_expressions(self):
        period = self.params.get('period', 14)
        return [
            "$close",
            f"Max($high, {period})",      # 修正 MAX -> Max
            f"Min($low, {period})",        # 修正 MIN -> Min
            "$factor"
        ]

    def get_condition(self, df):
        period = self.params.get('period', 14)
        threshold = self.params.get('threshold', -80)
        high_max = df[f"Max($high, {period})"]
        low_min = df[f"Min($low, {period})"]
        close = df["$close"]
        # 威廉指标公式：(最高价 - 收盘价) / (最高价 - 最低价) * -100
        wr = (high_max - close) / (high_max - low_min + 1e-10) * -100
        return wr < threshold

    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "Williams Oversold"        