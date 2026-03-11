# policies/rsi_oversold.py
from .base import BasePolicy

class Policy(BasePolicy):
    """
    RSI超卖策略：RSI低于阈值
    参数可在 config.yaml 的 policy_params 中设置：
        period: RSI计算周期（默认14）
        threshold: 超卖阈值（默认30）
    """
    def get_expressions(self):
        period = self.params.get('period', 14)
        # 返回收盘价、平均涨幅、平均跌幅、复权因子
        return [
            "$close",
            f"Mean(Max($close - Ref($close, 1), 0), {period})",
            f"Mean(Max(Ref($close, 1) - $close, 0), {period}) + 1e-10",
            "$factor"
        ]

    def get_condition(self, df):
        # 列索引：0:收盘价, 1:平均涨幅, 2:平均跌幅, 3:复权因子
        avg_gain = df.iloc[:, 1]
        avg_loss = df.iloc[:, 2]
        rsi = 100 - 100 / (1 + avg_gain / avg_loss)
        threshold = self.params.get('threshold', 30)
        return rsi < threshold

    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "RSI Oversold"        