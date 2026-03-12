# Qlib 选股框架

基于 Qlib 的选股工具，支持配置文件、自定义策略、多种股票池模式。

## 安装

1. 创建虚拟环境（推荐 Python 3.8+）
2. 安装依赖：`pip install -r requirements.txt`
3. 确保 Qlib 数据已准备就绪（配置 `config.yaml` 中的 `provider_uri`）

## 使用

```bash
# 查看帮助
bin/qselect --help

# 运行均线金叉策略（使用默认配置）
bin/qselect -p golden_cross

# 指定自定义股票池文件
bin/qselect -p golden_cross --pool-mode list --list-file stockpools/my_stocks.txt

# 静默模式（屏蔽 C++ 警告）
bin/qselect -p golden_cross -q

# 强制输出格式和stock pool要求一致，可以让其作为输入再次使用策略进行筛选
bin/qselect -p golden_cross -d 2026-02-25 --pool-mode all --outputpool
