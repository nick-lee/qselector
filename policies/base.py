# policies/base.py
class BasePolicy:
    """策略基类，所有具体策略需继承并实现以下方法"""
    def __init__(self, params=None):
        self.params = params or {}   # 存储策略参数

    def get_expressions(self):
        """返回因子表达式列表，每个表达式为字符串"""
        raise NotImplementedError

    def get_condition(self, df):
        """
        给定包含因子数据的DataFrame，返回布尔Series
        """
        raise NotImplementedError

    def get_name(self):
        """返回策略名称，默认使用类名"""
        return self.__class__.__name__