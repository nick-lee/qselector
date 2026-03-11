# policies/momentum_breakout.py
from .base import BasePolicy

class Policy(BasePolicy):
    """动量突破策略：收盘价突破 N 日最高价"""
    def get_expressions(self):
        lookback = self.params.get('lookback', 250)   # 默认250日
        return [
            "$close",
            f"Max($high, {lookback})",   # 动态生成表达式
            "$factor"
        ]

    def get_condition(self, df):
        # 列名与表达式对应
        cond = df["$close"] > df[f"Max($high, {self.params.get('lookback', 250)})"]
        return cond

    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "Momentum Breakout"        