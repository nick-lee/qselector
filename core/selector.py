# -*- coding: utf-8 -*-
import logging
import pandas as pd
from qlib.data import D
from tqdm import tqdm

logger = logging.getLogger(__name__)

def select_stocks(policy, stock_list, date, batch_size=50):
    """
    执行选股
    :param policy: 策略实例
    :param stock_list: 股票代码列表
    :param date: 选股日期 (YYYY-MM-DD)
    :param batch_size: 每批查询的股票数量
    :return: DataFrame，包含选中股票及其因子值，包含 'stock' 列
    """
    expressions = policy.get_expressions()
    logger.info(f"Expressions: {expressions}")
    logger.info(f"Total stocks to process: {len(stock_list)}")

    all_data = []
    total = len(stock_list)
    with tqdm(total=(total + batch_size - 1) // batch_size, desc="Processing batches", unit="batch") as pbar:
        for i in range(0, total, batch_size):
            batch = stock_list[i:i+batch_size]
            try:
                df_batch = D.features(batch, expressions, date, date)
                if df_batch is not None and not df_batch.empty:
                    all_data.append(df_batch)
            except Exception as e:
                logger.warning(f"Batch query failed for {batch[:5]}... : {e}")
            pbar.update(1)

    if not all_data:
        logger.warning("No data retrieved.")
        return pd.DataFrame()

    df = pd.concat(all_data)
    logger.info(f"Retrieved data for {len(df)} stocks.")

    # 应用筛选条件
    condition = policy.get_condition(df)
    selected_df = df[condition].copy()
    logger.info(f"Selected {len(selected_df)} stocks.")

    # 将索引（MultiIndex）转换为列
    selected_df = selected_df.reset_index()
    # 判断索引列的名称（Qlib 通常第一级为 datetime，第二级为 instrument）
    # 如果列名已知，直接使用；否则按位置假设第一列为日期，第二列为股票代码
    if 'datetime' in selected_df.columns and 'instrument' in selected_df.columns:
        selected_df.rename(columns={'instrument': 'stock'}, inplace=True)
        selected_df.drop(columns=['datetime'], inplace=True)
    else:
        # 按位置处理：假设第一列是日期，第二列是股票代码
        cols = selected_df.columns.tolist()
        selected_df.rename(columns={cols[0]: 'datetime', cols[1]: 'stock'}, inplace=True)
        selected_df.drop(columns=['datetime'], inplace=True)

    return selected_df