# policies/bb_breakout.py
from .base import BasePolicy

class Policy(BasePolicy):
    """
    布林带突破策略：收盘价突破布林带上轨（或跌破下轨）
    参数可在 config.yaml 的 policy_params 中设置：
        period: 布林带计算周期（默认20）
        width: 标准差倍数（默认2.0）
        direction: 突破方向，"upper" 表示突破上轨（默认），"lower" 表示跌破下轨
    """
    def get_expressions(self):
        period = self.params.get('period', 20)
        return [
            "$close",
            f"Mean($close, {period})",                # 中轨
            f"Std($close, {period})",                 # 标准差
            "$factor"
        ]

    def get_condition(self, df):
        period = self.params.get('period', 20)
        width = self.params.get('width', 2.0)
        direction = self.params.get('direction', 'upper')

        mid = df[f"Mean($close, {period})"]
        std = df[f"Std($close, {period})"]
        close = df["$close"]

        if direction == 'upper':
            return close > mid + width * std
        else:
            return close < mid - width * std