# -*- coding: utf-8 -*-
import os
import logging
from qlib.data import D

logger = logging.getLogger(__name__)

def load_stock_pool(config: dict):
    """
    根据配置加载股票列表
    支持的模式：
        - index : 从 Qlib 内置指数或本地 instruments 文件加载成分股
        - all   : 全市场所有股票（包含北交所）
        - main  : 仅 sh/sz 开头的股票（主板+中小创）
        - top_n : 从指定来源取前 N 只
        - list  : 从自定义文件读取股票列表
    """
    mode = config['stock_pool']['mode']
    provider_uri = config['qlib']['provider_uri']
    logger.info(f"Loading stock pool with mode: {mode}")

    if mode == 'index':
        index_name = config['stock_pool'].get('index_name', 'csi300')
        logger.info(f"Using index name: {index_name} (default: csi300)")
        # 尝试通过 Qlib API 获取
        stocks = list(D.instruments(market=index_name))
        logger.debug(f"D.instruments returned: {stocks[:5]}")

        # 检查返回的列表是否有效（通常应包含股票代码，如 'sh600000'）
        if not stocks or (len(stocks) == 2 and stocks[0] == 'market' and stocks[1] == 'filter_pipe'):
            logger.warning(f"Instruments API returned unexpected result for '{index_name}', falling back to direct file read.")
            # 从本地 instruments 文件读取
            file_path = os.path.join(provider_uri, 'instruments', f"{index_name}.txt")
            logger.info(f"Reading from file: {file_path}")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Instrument file not found: {file_path}")

            # 读取所有行
            raw_lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_lines = f.readlines()
            logger.info(f"File contains {len(raw_lines)} lines (including comments and blanks).")

            # 解析股票代码
            code_set = set()
            for line in raw_lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if parts:
                    code_set.add(parts[0])
            logger.info(f"After parsing, unique stock codes: {len(code_set)}")

            stocks = list(code_set)
            logger.info(f"Loaded {len(stocks)} unique stocks from {file_path}")
        else:
            # 过滤可能的无效条目
            stocks = [s for s in stocks if s and isinstance(s, str) and not s.startswith('market')]
            logger.info(f"Loaded {len(stocks)} stocks from index {index_name} via API")

        logger.info(f"Final stock list count for index {index_name}: {len(stocks)}")
        return stocks

    elif mode == 'all':
        features_dir = os.path.join(provider_uri, 'features')
        stocks = [d for d in os.listdir(features_dir)
                  if os.path.isdir(os.path.join(features_dir, d))]
        logger.info(f"Loaded {len(stocks)} stocks from all market")
        return stocks

    elif mode == 'main':
        features_dir = os.path.join(provider_uri, 'features')
        all_stocks = [d for d in os.listdir(features_dir)
                      if os.path.isdir(os.path.join(features_dir, d))]
        stocks = [s for s in all_stocks if s.startswith(('sh', 'sz'))]
        logger.info(f"Loaded {len(stocks)} main board stocks (sh/sz)")
        return stocks

    elif mode == 'top_n':
        n = config['stock_pool']['top_n']
        source = config['stock_pool'].get('source', 'main')
        features_dir = os.path.join(provider_uri, 'features')
        all_stocks = [d for d in os.listdir(features_dir)
                      if os.path.isdir(os.path.join(features_dir, d))]

        if source == 'main':
            base_stocks = [s for s in all_stocks if s.startswith(('sh', 'sz'))]
        else:  # source == 'all'
            base_stocks = all_stocks

        stocks = base_stocks[:n]
        logger.info(f"Loaded top {len(stocks)} stocks from {source}")
        return stocks

    elif mode == 'list':
        list_file = config['stock_pool']['list_file']
        if not os.path.isabs(list_file):
            # 相对于项目根目录（假设当前工作目录为项目根）
            list_file = os.path.join(os.getcwd(), list_file)
        if not os.path.exists(list_file):
            raise FileNotFoundError(f"List file not found: {list_file}")
        stocks = []
        with open(list_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    stocks.append(parts[0])
        # 可选去重
        stocks = list(dict.fromkeys(stocks))  # 保持顺序的去重
        logger.info(f"Loaded {len(stocks)} stocks from list file {list_file}")
        return stocks

    else:
        raise ValueError(f"Unknown stock pool mode: {mode}")