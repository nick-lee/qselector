# policies/golden_cross.py
from .base import BasePolicy

class Policy(BasePolicy):
    def get_expressions(self):
        short = self.params.get('short', 5)
        long = self.params.get('long', 20)
        return [
            "$close",
            f"Mean($close, {short})",
            f"Mean($close, {long})",
            "$factor"
        ]

    def get_condition(self, df):
        short = self.params.get('short', 5)
        long = self.params.get('long', 20)
        return df[f"Mean($close, {short})"] > df[f"Mean($close, {long})"]
        
    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "GoldenCross"        