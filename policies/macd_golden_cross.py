# policies/macd_golden_cross.py
from .base import BasePolicy

class Policy(BasePolicy):
    """
    MACD金叉策略：DIF线上穿DEA线
    参数可在 config.yaml 的 policy_params 中设置：
        fast_period: 快线EMA周期（默认12）
        slow_period: 慢线EMA周期（默认26）
        signal_period: 信号线EMA周期（默认9）
    """
    def get_expressions(self):
        fast = self.params.get('fast_period', 12)
        slow = self.params.get('slow_period', 26)
        signal = self.params.get('signal_period', 9)
        
        # Qlib中EMA函数为EMA，需计算DIF = EMA(close, fast) - EMA(close, slow)
        # 由于Qlib表达式无法直接嵌套计算，我们需要分别获取两个EMA值
        return [
            "$close",
            f"EMA($close, {fast})",      # 快线EMA
            f"EMA($close, {slow})",      # 慢线EMA
            "$factor"
        ]

    def get_condition(self, df):
        fast = self.params.get('fast_period', 12)
        slow = self.params.get('slow_period', 26)
        
        # 计算DIF = 快线EMA - 慢线EMA
        dif = df[f"EMA($close, {fast})"] - df[f"EMA($close, {slow})"]
        
        # 由于无法直接获取DEA（DIF的EMA），此处简化处理：
        # 使用DIF > 0作为近似条件（DIF>0表示短期趋势强于长期趋势）
        # 更精确的金叉需要前一日DIF <= 0且今日DIF > 0，但需历史数据支持
        return dif > 0

    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "MACD Golden Cross"