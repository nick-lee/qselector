## 已实现策略列表

| 策略名称       | 文件                   | 核心逻辑                  | 关键参数                                                     | 适用场景               |
| :------------- | :--------------------- | :------------------------ | :----------------------------------------------------------- | :--------------------- |
| **均线金叉**   | `golden_cross.py`      | 短期均线上穿长期均线      | `short`(默认5), `long`(默认20)                               | 趋势跟踪，捕捉上涨启动 |
| **RSI超卖**    | `rsi_oversold.py`      | RSI低于阈值，超跌反弹     | `period`(14), `threshold`(30)                                | 超跌反弹，左侧交易     |
| **趋势动量**   | `momentum_trend.py`    | 过去N日涨幅超过阈值       | `lookback`(60), `min_return`(0.05)                           | 强者恒强，趋势延续     |
| **成交量异动** | `volume_surge.py`      | 成交量放大到均量的倍数    | `lookback`(20), `threshold`(2.0)                             | 资金异动，量价配合     |
| **布林带突破** | `bb_breakout.py`       | 突破布林带上轨或下轨      | `period`(20), `width`(2.0), `direction`(upper)               | 趋势加速，突破确认     |
| **MACD金叉**   | `macd_golden_cross.py` | DIF > 0（快线在慢线上方） | `fast_period`(12), `slow_period`(26)                         | 动能确认，趋势加强     |
| **威廉超卖**   | `williams_oversold.py` | 威廉指标低于阈值          | `period`(14), `threshold`(-80)                               | 超卖反弹，对价格敏感   |
| **底部放量**   | `bottom_volume.py`     | 低位 + 放量               | `ma_period`(250), `max_price_ratio`(0.9), `volume_threshold`(2.0) | 底部启动，反转信号     |

## 🔧 参数配置示例

在 `config.yaml` 中配置策略参数：

yaml

```
policy_params:
  golden_cross:
    short: 10
    long: 30
  rsi_oversold:
    period: 14
    threshold: 25
  momentum_trend:
    lookback: 60
    min_return: 0.1
  volume_surge:
    lookback: 20
    threshold: 1.5
```



## 🎯 策略选择建议

| 交易风格     | 推荐策略                      | 组合建议                                   |
| :----------- | :---------------------------- | :----------------------------------------- |
| **短线交易** | RSI超卖、威廉超卖、成交量异动 | RSI超卖 + 成交量异动                       |
| **中线波段** | 均线金叉、MACD金叉            | 均线金叉 + MACD金叉                        |
| **长线持有** | 趋势动量、底部放量            | 趋势动量 + 底部放量                        |
| **组合策略** | 多策略加权                    | 趋势动量(0.4) + RSI超卖(0.3) + 成交量(0.3) |

每个策略都可以独立运行，也可以通过组合策略实现更复杂的选股逻辑。