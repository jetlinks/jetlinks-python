from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

T = TypeVar('T')


class Logger(ABC):
    """日志记录器接口"""
    
    @abstractmethod
    def debug(self, message: str, *args: Any) -> None:
        """
        记录调试日志
        :param message: 日志消息
        :param args: 参数
        """
        pass
    
    @abstractmethod
    def info(self, message: str, *args: Any) -> None:
        """
        记录信息日志
        :param message: 日志消息
        :param args: 参数
        """
        pass
    
    @abstractmethod
    def warn(self, message: str, *args: Any) -> None:
        """
        记录警告日志
        :param message: 日志消息
        :param args: 参数
        """
        pass
    
    @abstractmethod
    def error(self, message: str, *args: Any) -> None:
        """
        记录错误日志
        :param message: 日志消息
        :param args: 参数
        """
        pass
    
    @abstractmethod
    def trace(self, message: str, *args: Any) -> None:
        """
        记录跟踪日志
        :param message: 日志消息
        :param args: 参数
        """
        pass


class Metrics(ABC):
    """指标接口"""
    
    @abstractmethod
    def count(self, operation: str, inc: int) -> None:
        """
        记录计数指标
        :param operation: 操作名称
        :param inc: 增量
        """
        pass
    
    @abstractmethod
    def value(self, operation: str, value: int) -> None:
        """
        记录值指标
        :param operation: 操作名称
        :param value: 值
        """
        pass
    
    @abstractmethod
    def error(self, operation: str, error: Exception) -> None:
        """
        记录错误指标
        :param operation: 操作名称
        :param error: 错误
        """
        pass


class Tracer(ABC):
    """跟踪器接口"""
    
    @abstractmethod
    def trace(self, operation: str, callback: Callable[[], T]) -> T:
        """
        跟踪操作
        :param operation: 操作名称
        :param callback: 回调函数
        :return: 回调函数的返回值
        """
        pass


class Monitor(ABC):
    """监控接口"""
    
    @abstractmethod
    def logger(self) -> Logger:
        """
        获取日志记录器
        :return: 日志记录器
        """
        pass
    
    @abstractmethod
    def metrics(self) -> Metrics:
        """
        获取指标记录器
        :return: 指标记录器
        """
        pass
    
    @abstractmethod
    def tracer(self) -> Tracer:
        """
        获取跟踪器
        :return: 跟踪器
        """
        pass 