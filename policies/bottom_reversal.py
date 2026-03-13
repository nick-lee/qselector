# policies/bottom_reversal.py
from .base import BasePolicy
import pandas as pd

class Policy(BasePolicy):
    """
    左侧埋伏策略：捕捉底部反转的先机
    参数可在 config.yaml 的 policy_params 中设置：
        bottom_period: 底部观察期（默认60日）
        max_volatility: 最大波动幅度（默认0.3，即30%）
        volume_increase: 放量倍数（默认1.2，即温和放量20%）
        ma_convergence: 均线收敛阈值（默认0.03，即3%）
        max_price_ratio: 股价相对于年线的最大比例（默认1.2，即低于年线20%）
        min_days_since_low: 距离最低点的最小天数（默认20日）
        min_score: 得分制阈值（默认3）
        use_score_fallback: 是否启用得分制降级（默认True）
    """
    def get_expressions(self):
        period = self.params.get('bottom_period', 60)
        return [
            "$close",
            "$low", 
            "$high",
            "$volume",
            f"Min($low, {period})",
            f"Max($high, {period})",
            "Mean($close, 5)",
            "Mean($close, 10)",
            "Mean($close, 20)",
            "Mean($close, 250)",
            "Mean($volume, 20)",
            "Ref($close, 20)",
            "$factor"
        ]

    def get_condition(self, df: pd.DataFrame) -> pd.Series:
        # ==================== 获取参数 ====================
        bottom_period = self.params.get('bottom_period', 60)  # 新增
        max_volatility = self.params.get('max_volatility', 0.3)
        volume_increase = self.params.get('volume_increase', 1.05)
        ma_convergence = self.params.get('ma_convergence', 0.05)
        max_price_ratio = self.params.get('max_price_ratio', 1.2)
        min_score = self.params.get('min_score', 3)
        use_score_fallback = self.params.get('use_score_fallback', False)

        # 打印当前使用的参数
        print(f"当前参数: bottom_period={self.params.get('bottom_period', 60)}")
        print(f"当前参数: max_volatility={self.params.get('max_volatility', 0.3)}")
        print(f"当前参数: volume_increase={self.params.get('volume_increase', 1.05)}")
        print(f"当前参数: use_score_fallback={self.params.get('use_score_fallback', True)}")
        # ==================== 提取数据 ====================
        close = df["$close"]
        low = df["$low"]
        high = df["$high"]
        volume = df["$volume"]
        # 使用动态周期
        low_period = df[f"Min($low, {bottom_period})"]
        high_period = df[f"Max($high, {bottom_period})"]
        ma5 = df["Mean($close, 5)"]
        ma10 = df["Mean($close, 10)"]
        ma20 = df["Mean($close, 20)"]
        ma250 = df["Mean($close, 250)"]
        volume_ma20 = df["Mean($volume, 20)"]
        close_20d_ago = df["Ref($close, 20)"]

        # ==================== 计算各个条件 ====================
        # 1. 底部盘旋：N日内波动幅度小于阈值
        volatility = (high_period - low_period) / (low_period + 1e-10)
        cond1 = volatility < max_volatility

        # 2. 温和放量：成交量大于20日均量，但不过度
        volume_ratio = volume / (volume_ma20 + 1e-10)
        cond2 = (volume_ratio > volume_increase) & \
                (volume_ratio < volume_increase + 0.5)

        # 3. 均线聚合：均线之间的最大距离小于阈值
        ma_diff = (ma5 - ma20).abs() / (ma20 + 1e-10)
        cond3 = ma_diff < ma_convergence

        # 4. 仍在低位：股价低于年线一定比例
        cond4 = close < ma250 * max_price_ratio

        # 5. 筑底确认：已脱离最低点（不低于N日最低点2%）
        cond5 = close > low_period * 1.02

        # 6. 跌幅收敛：最近20日跌幅小于5%
        recent_return = (close - close_20d_ago) / (close_20d_ago + 1e-10)
        cond6 = recent_return > -0.05
        print(f"cond1 满足: {cond1.sum()}/{len(df)}")
        print(f"cond2 满足: {cond2.sum()}/{len(df)}")
        print(f"cond3 满足: {cond3.sum()}/{len(df)}")
        print(f"cond4 满足: {cond4.sum()}/{len(df)}")
        print(f"cond5 满足: {cond5.sum()}/{len(df)}")
        print(f"cond6 满足: {cond6.sum()}/{len(df)}")

        # ==================== 严格条件 ====================
        strict_result = cond1 & cond2 & cond3 & cond4 & cond5 & cond6
        strict_count = strict_result.sum()

        # 如果有严格条件的结果，直接返回
        if strict_count > 0:
            print(f"✓ 严格条件选出 {strict_count} 只股票")
            return strict_result

        # ==================== 得分制降级 ====================
        if not use_score_fallback:
            print("⚠️ 严格条件无结果，且未启用得分制降级")
            return pd.Series(False, index=df.index)

        print(f"\n⚠️ 严格条件无结果，使用得分制选出备选股票")

        # 计算得分（每个条件1分）
        score = pd.Series(0, index=df.index)
        score += cond1.astype(int)
        score += cond2.astype(int)
        score += cond3.astype(int)
        score += cond4.astype(int)
        score += cond5.astype(int)
        score += cond6.astype(int)

        # 输出得分分布（从高到低）
        print("\n得分分布：")
        for threshold in range(6, 0, -1):
            count = (score >= threshold).sum()
            if count > 0:
                print(f"  得分 ≥{threshold}: {count} 只")

        # 返回得分≥阈值的股票
        result = score >= min_score
        print(f"\n✓ 得分制选出 {(result).sum()} 只股票（得分 ≥{min_score}）")

        # 打印得分≥5的股票代码（前10只）
        high_score_mask = score >= 5
        high_score_count = high_score_mask.sum()
        if high_score_count > 0:
            # 先查看索引的结构
            print(f"索引层级数: {df.index.nlevels}")
            print(f"索引名称: {df.index.names}")
            print(f"第一层样例: {df.index.get_level_values(0)[:3].tolist()}")
            print(f"第二层样例: {df.index.get_level_values(1)[:3].tolist()}")            
            # 直接从df的索引中获取股票代码
            stock_codes = df.index.get_level_values(0)[high_score_mask].tolist()
            print(f"\n得分≥5的股票（前10只）：")
            for i, code in enumerate(stock_codes[:10]):
                print(f"  {i+1}. {code}")
            if high_score_count > 10:
                print(f"  ... 共 {high_score_count} 只")
        return result

    def get_name(self):
        """返回策略名称，用于输出文件"""
        return "Bottom Reversal"                