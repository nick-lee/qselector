# QSelector - 基于 Qlib 的量化选股框架

https://img.shields.io/badge/python-3.8+-blue.svg
https://img.shields.io/badge/qlib-0.9.7-green.svg
https://img.shields.io/badge/license-MIT-yellow.svg

## 📌 项目简介

QSelector 是一个基于 Microsoft Qlib 构建的量化选股框架，旨在为量化爱好者提供一个简单、可扩展的选股工具。通过配置文件管理和命令行操作，您可以快速运行多种经典量化策略，筛选出符合条件的股票，并输出结果到 CSV 文件，代码基本有AI完成，不足之处可以共同改进。

**⚠️ 重要声明：本项目的所有策略和输出结果仅供学习参考，不构成任何投资建议。股市有风险，投资需谨慎！**

## ✨ 核心特性

- **🎯 策略即插即用**：通过简单的 Python 文件即可添加新策略，无需修改框架代码
- **⚙️ 灵活配置**：YAML 配置文件管理数据源、股票池、策略参数等
- **📊 多种股票池**：支持指数成分股、全市场、自定义列表等多种模式
- **📈 经典策略库**：内置趋势动量、RSI超卖、均线金叉等常用策略
- **🔄 自动日期处理**：自动调整到最近交易日，提醒数据时效性
- **🎨 彩色日志**：不同级别日志用颜色区分，提升可读性
- **📁 唯一输出文件**：每次运行生成带时间戳的 CSV 文件，避免覆盖

## 🚀 快速开始

### 安装

bash

```
# 克隆项目
git clone https://github.com/nick-lee/qselector.git
cd qselector

# 安装依赖
pip install -r requirements.txt
```



### 配置数据路径

编辑 `config/config.yaml`，设置您的 Qlib 数据路径：

yaml

```
qlib:
  provider_uri: "D:/path/to/your/qlib_data"
  region: "cn"
```

数据可以从 `https://github.com/chenditc/investment_data/releases/latest` 感谢社区能提供数据！

### 运行示例

bash

```
# 运行均线金叉策略
bin/qselect -p golden_cross

# 指定日期运行
bin/qselect -p rsi_oversold -d 2026-03-09

# 使用自定义股票池
bin/qselect -p momentum_trend --pool-mode list --list-file stockpools/my_stocks.txt
```



## 📁 项目结构

text

```
qselector/
├── bin/
│   └── qselect                 # 命令行入口
├── config/
│   └── config.yaml             # 主配置文件
├── core/
│   ├── qlib_init.py            # Qlib初始化
│   ├── data_loader.py          # 股票池加载器
│   ├── selector.py             # 选股执行器
│   └── date_utils.py           # 日期工具
├── policies/
│   ├── base.py                 # 策略基类
│   ├── golden_cross.py         # 均线金叉
│   ├── rsi_oversold.py         # RSI超卖
│   ├── momentum_trend.py       # 趋势动量
│   ├── volume_surge.py         # 成交量异动
│   ├── bb_breakout.py          # 布林带突破
│   ├── macd_golden_cross.py    # MACD金叉
│   ├── williams_oversold.py    # 威廉指标超卖
│   └── bottom_volume.py        # 底部放量
├── stockpools/                  # 自定义股票池
│   └── my_stocks.txt
├── outputs/                     # 选股结果输出
└── requirements.txt
```



## 📊 内置策略说明

| 策略名称   | 文件                   | 核心逻辑             | 参数                                               |
| :--------- | :--------------------- | :------------------- | :------------------------------------------------- |
| 趋势动量   | `momentum_trend.py`    | 过去N日涨幅 > 阈值   | `lookback`, `min_return`                           |
| RSI超卖    | `rsi_oversold.py`      | RSI低于阈值          | `period`, `threshold`                              |
| 均线金叉   | `golden_cross.py`      | 短期均线上穿长期均线 | `short`, `long`                                    |
| 成交量异动 | `volume_surge.py`      | 成交量 > 均量 × 阈值 | `lookback`, `threshold`                            |
| 布林带突破 | `bb_breakout.py`       | 突破布林带上/下轨    | `period`, `width`, `direction`                     |
| MACD金叉   | `macd_golden_cross.py` | DIF > 0              | `fast_period`, `slow_period`                       |
| 威廉超卖   | `williams_oversold.py` | 威廉指标低于阈值     | `period`, `threshold`                              |
| 底部放量   | `bottom_volume.py`     | 低位 + 放量          | `ma_period`, `max_price_ratio`, `volume_threshold` |

## ⚙️ 配置文件说明

### 数据配置

yaml

```
qlib:
  provider_uri: "数据路径"
  region: "cn"
  quiet: false  # 是否屏蔽C++警告
```



### 股票池配置

yaml

```
stock_pool:
  mode: "index"        # index / all / main / top_n / list
  index_name: "csi300" # mode=index时有效
  top_n: 1000          # mode=top_n时有效
  list_file: "stockpools/my_stocks.txt" # mode=list时有效
```

all ： 表示从全股票池子中选择； 



### 策略参数配置

yaml

```
policy_params:
  golden_cross:
    short: 5
    long: 20
  rsi_oversold:
    period: 14
    threshold: 30
```



## 📝 添加新策略

1. 在 `policies/` 下新建 `.py` 文件，继承 `BasePolicy`
2. 实现 `get_expressions()` 返回因子表达式列表
3. 实现 `get_condition(df)` 返回筛选条件
4. （可选）在配置文件中添加策略参数

python

```
from .base import BasePolicy

class Policy(BasePolicy):
    def get_expressions(self):
        return ["$close", "Mean($close, 5)", "$factor"]
    
    def get_condition(self, df):
        return df["Mean($close, 5)"] > df["$close"]
```



## ⚠️ 风险提示

1. **数据风险**：本工具依赖 Qlib 数据源，数据准确性、完整性可能影响选股结果
2. **策略风险**：内置策略仅为经典策略的简单实现，未经充分回测验证，实盘使用风险自负
3. **技术风险**：本工具仅供学习研究，不保证程序的稳定性和可靠性
4. **市场风险**：历史表现不代表未来收益，股市有风险，投资需谨慎

## 📜 开源协议

本项目基于 MIT 协议开源，仅供学习交流，**严禁用于商业用途**。

## 🙏 致谢

- [Microsoft Qlib](https://github.com/microsoft/qlib) - 优秀的开源量化平台
- 所有贡献者和用户的支持

------

**如果这个项目对您有帮助，欢迎 Star 支持！** ⭐