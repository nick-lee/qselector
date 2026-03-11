# -*- coding: utf-8 -*-
import sys
import os
import logging
from contextlib import contextmanager
import qlib
from qlib.config import REG_CN

logger = logging.getLogger(__name__)

@contextmanager
def stderr_redirect(quiet: bool = False):
    """临时重定向 stderr，用于屏蔽 C++ 扩展的直接输出"""
    if not quiet:
        yield
        return
    try:
        original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

def init(config: dict):
    """初始化 Qlib，支持安静模式"""
    provider_uri = config['qlib']['provider_uri']
    region = config['qlib'].get('region', 'cn')
    quiet = config['qlib'].get('quiet', False)

    logger.info(f"Initializing Qlib with provider_uri: {provider_uri}, region: {region}, quiet: {quiet}")
    with stderr_redirect(quiet):
        qlib.init(provider_uri=provider_uri, region=region)
    logger.info("Qlib initialized successfully.")