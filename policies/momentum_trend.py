# policies/momentum_trend.py
from .base import BasePolicy

class Policy(BasePolicy):
    """
    趋势动量策略（时序动量）：过去 N 日涨幅 > 阈值（默认 0，即上涨）
    参数可在 config.yaml 的 policy_params 中设置：
        lookback: 回看天数（默认 60）
        min_return: 最小涨幅阈值（默认 0.0，要求涨幅 > 0）
    """
    def get_expressions(self):
        lookback = self.params.get('lookback', 60)
        return [
            "$close",
            f"$close / Ref($close, {lookback}) - 1",   # 过去 N 日涨幅（正确方向）
            "$factor"
        ]

    def get_condition(self, df):
        lookback = self.params.get('lookback', 60)
        ret_col = f"$close / Ref($close, {lookback}) - 1"
        min_return = self.params.get('min_return', 0.0)
        print(f"当前使用的 min_return = {min_return}")
        return df[ret_col] >= min_return

    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "Momentum Trend"        