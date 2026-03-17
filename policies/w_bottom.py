# policies/w_bottom.py
# -*- coding: utf-8 -*-
"""
W底（双重底）反转策略
识别条件：
1. 左底：过去N1日最低点，且前期有足够跌幅
2. 右底：过去N2日最低点，且不低于左底 * (1 - tolerance)
3. 间隔：左右底相隔 min_gap 到 max_gap 个交易日
4. 量能：右底处成交量萎缩 < volume_shrink * MA20
5. 突破：收盘价站上颈线 * (1 + breakout_threshold)
6. 确认：突破时放量 > volume_surge * MA20

参数配置（可在 config.yaml 中设置）：
    lookback_left: 20      # 左底回看期
    lookback_right: 15     # 右底回看期
    bottom_tolerance: 0.02 # 底差容忍度 (2%)
    min_gap: 5             # 最小间隔
    max_gap: 30            # 最大间隔
    drop_threshold: -0.10  # 左底前跌幅要求
    volume_shrink: 0.7     # 右底缩量阈值
    breakout_threshold: 0.01 # 突破确认幅度 (1%)
    volume_surge: 1.5      # 突破放量倍数
    confirm_days: 1        # 突破确认天数
"""
from .base import BasePolicy
import pandas as pd
import numpy as np

class Policy(BasePolicy):
    
    # 默认参数（可作为基准）
    DEFAULT_PARAMS = {
        # 形态参数
        'lookback_left': 30,      # 左底回看期
        'lookback_right': 20,     # 右底回看期
        'bottom_tolerance': 0.05, # 底差容忍度 (5%)
        'min_gap': 3,             # 最小间隔（日）
        'max_gap': 40,            # 最大间隔（日）
        'drop_threshold': -0.05,  # 左底前跌幅要求
        
        # 量能参数
        'volume_shrink': 0.8,     # 右底缩量阈值
        'volume_surge': 1.3,      # 突破放量倍数
        
        # 突破参数
        'breakout_threshold': 0.01, # 突破确认幅度 (1%)
        
        # 调试参数
        'verbose': False,          # 是否打印详细信息
    }
    
    def __init__(self, params=None):
        # 合并默认参数和用户参数
        merged_params = self.DEFAULT_PARAMS.copy()
        if params:
            merged_params.update(params)
        super().__init__(merged_params)
    
    def get_expressions(self):
        """返回需要的所有基础表达式"""
        return [
            "$close", "$high", "$low", "$volume",
            "Mean($volume,20)",  # 20日均量
            "Ref($close,10)",    # 10日前的收盘价
        ]
    
    def _check_breakout_volume(self, volume, vol_ma20):
        """检查突破放量"""
        threshold = self.params['volume_surge']
        ratio = volume / vol_ma20 if vol_ma20 > 0 else 0
        passed = ratio >= threshold
        
        if self.params['verbose'] and not passed:
            print(f"    突破放量: {ratio:.2f} < {threshold} (需要 ≥{threshold})")
        return passed
    
    def _check_price_gap(self, left_price, right_price):
        """检查左右底价格关系"""
        tolerance = self.params['bottom_tolerance']
        min_ratio = 1 - tolerance
        
        # 右底不低于左底的 (1-tolerance)
        passed = right_price >= left_price * min_ratio
        
        if self.params['verbose'] and not passed:
            print(f"    右底过低: {right_price:.2f} < {left_price:.2f} * {min_ratio:.2f}")
        return passed
    
    def _check_gap_days(self, gap):
        """检查间隔天数"""
        min_gap = self.params['min_gap']
        max_gap = self.params['max_gap']
        passed = min_gap <= gap <= max_gap
        
        if self.params['verbose'] and not passed:
            print(f"    间隔天数: {gap} (需在{min_gap}-{max_gap}之间)")
        return passed
    
    def _check_prior_drop(self, df, left_idx):
        """检查左底前跌幅"""
        threshold = self.params['drop_threshold']
        
        if left_idx < 10:
            return True  # 数据不足时默认通过
        
        close_10d_before = df.iloc[left_idx-10]['$close']
        left_price = df.iloc[left_idx]['$low']
        drop = (left_price / close_10d_before - 1)
        
        passed = drop <= threshold  # 跌幅足够大（负值）
        
        if self.params['verbose'] and not passed:
            print(f"    前期跌幅: {drop:.2%} > {threshold:.2%}")
        return passed
    
    def _check_right_bottom_volume(self, df, right_idx):
        """检查右底缩量"""
        threshold = self.params['volume_shrink']
        
        vol = df.iloc[right_idx]['$volume']
        vol_ma = df.iloc[right_idx]['Mean($volume,20)']
        ratio = vol / vol_ma if vol_ma > 0 else 1
        
        passed = ratio <= threshold
        
        if self.params['verbose'] and not passed:
            print(f"    右底缩量: {ratio:.2f} > {threshold}")
        return passed
    
    def _find_neckline(self, df, left_idx, right_idx):
        """找左右底之间的最高点（颈线）"""
        window = df.iloc[left_idx:right_idx+1]
        return window['$high'].max()
    
    def _check_breakout(self, current_close, neckline):
        """检查是否突破颈线"""
        threshold = self.params['breakout_threshold']
        required = neckline * (1 + threshold)
        passed = current_close >= required
        
        if self.params['verbose'] and not passed:
            print(f"    突破颈线: {current_close:.2f} < {required:.2f   } (颈线{neckline:.2f}+{threshold:.1%})")
        return passed
            
    def _check_w_bottom(self, df, idx):
        """检查指定索引是否形成W底（只保留关键LOG）"""
        # 关闭详细打印
        verbose = False  # 改为False
        
        if verbose:
            print(f"\n  ====== 开始检查第{idx}行 ======")
            print(f"  📊 数据总行数: {len(df)}")
        
        # 获取当前日期的数据
        current_close = df.iloc[idx]['$close']
        current_volume = df.iloc[idx]['$volume']
        vol_ma20 = df.iloc[idx]['Mean($volume,20)']
        
        # 1. 检查突破放量
        vol_ratio = current_volume / vol_ma20 if vol_ma20 > 0 else 0
        if vol_ratio < self.params['volume_surge']:
            return False
        
        # 如果数据不足，无法形成W底
        if len(df) < 20:
            return False
        
        # 在当前日期前寻找W底形态
        found_any = False
        checked_count = 0
        
        # 遍历可能的右底位置
        max_right = min(60, idx)
        for right_offset in range(self.params['min_gap'], max_right + 1):
            right_idx = idx - right_offset
            if right_idx < 0:
                continue
            
            right_price = df.iloc[right_idx]['$low']
            right_volume = df.iloc[right_idx]['$volume']
            right_vol_ma = df.iloc[right_idx]['Mean($volume,20)']
            
            # 遍历可能的左底位置
            max_left = min(right_offset + self.params['max_gap'], idx)
            for left_offset in range(right_offset + self.params['min_gap'], max_left + 1):
                left_idx = idx - left_offset
                if left_idx < 0:
                    continue
                
                left_price = df.iloc[left_idx]['$low']
                checked_count += 1
                gap = left_offset - right_offset
                
                # 2. 检查左右底价格关系
                tolerance = self.params['bottom_tolerance']
                min_ratio = 1 - tolerance
                if right_price < left_price * min_ratio:
                    continue
                
                # 3. 检查间隔天数
                if not (self.params['min_gap'] <= gap <= self.params['max_gap']):
                    continue
                
                # 4. 检查左底前跌幅
                if left_idx >= 10:
                    close_10d_before = df.iloc[left_idx-10]['$close']
                    drop = (left_price / close_10d_before - 1)
                    if drop > self.params['drop_threshold']:
                        continue
                
                # 5. 检查右底缩量
                vol_shrink_ratio = right_volume / right_vol_ma if right_vol_ma > 0 else 1
                if vol_shrink_ratio > self.params['volume_shrink']:
                    continue
                
                # 6. 找颈线
                window = df.iloc[left_idx:right_idx+1]
                neckline = window['$high'].max()
                
                # 7. 检查是否突破颈线
                required = neckline * (1 + self.params['breakout_threshold'])
                if current_close < required:
                    continue
                
                # 所有条件满足
                if True:  # 只打印最终发现的结果
                    print(f"\n      🎉 发现有效W底!")
                    print(f"        左底: {left_price:.4f} @-{left_offset}天")
                    print(f"        右底: {right_price:.4f} @-{right_offset}天")
                    print(f"        颈线: {neckline:.4f}")
                    print(f"        间隔: {gap}天")
                
                return True
        
        return False
                

    def get_condition(self, df):
        self.params['verbose'] = True
        
        print(f"\n{'='*60}")
        print(f"W底策略分析 - 总股票数: {len(df)}")
        print(f"当前参数: { {k:v for k,v in self.params.items() if k != 'verbose'} }")
        print(f"{'='*60}")
        
        # 调试信息
        print(f"df索引类型: {type(df.index)}")
        print(f"df索引样例: {df.index[0]}")
        print(f"df列名: {df.columns.tolist()}")
        
        # 统计全部股票池分布
        stock_types = {'sh':0, 'sz':0, 'bj':0, 'other':0}
        for idx in df.index:
            if isinstance(idx, tuple) and len(idx) >= 2:
                code = idx[0]
                if code.startswith('sh'): stock_types['sh'] += 1
                elif code.startswith('sz'): stock_types['sz'] += 1
                elif code.startswith('bj'): stock_types['bj'] += 1
                else: stock_types['other'] += 1
        
        print(f"全市场股票分布: 沪={stock_types['sh']}, 深={stock_types['sz']}, 北={stock_types['bj']}, 其他={stock_types['other']}")
        
        # 创建结果Series
        result = pd.Series(False, index=df.index)
        
        # 分析全部股票（从第30只开始，因为需要历史数据）
        start_idx = 30
        print(f"\n分析全部股票 (从索引{start_idx}开始, 共{len(df)-start_idx}只)...")
        
        count = 0
        for i in range(start_idx, len(df)):  # 改为分析全部
            idx_label = df.index[i]
            stock_code = idx_label[1] if isinstance(idx_label, tuple) and len(idx_label) >= 2 else str(idx_label)
            
            if self._check_w_bottom(df, i):
                result.iloc[i] = True
                count += 1
                print(f"\n✅ 发现W底! {stock_code} (索引:{i})")
        
        print(f"\n{'='*60}")
        print(f"分析完成: 发现 {count} 只股票形成W底")
        print(f"{'='*60}")
        
        return result
        
    
    def get_name(self):
        return "WBottomStrategy"