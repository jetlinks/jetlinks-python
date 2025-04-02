from abc import ABC, abstractmethod
from typing import Dict, Any, List, TypeVar, Generic, Optional

import rx
from rx import Observable

from .command import Command
from ..metadata.function_metadata import FunctionMetadata

T = TypeVar('T')
R = TypeVar('R')


class CommandSupport(ABC):
    """命令支持接口"""
    
    @abstractmethod
    def execute(self, command: Command[T]) -> Observable:
        """
        执行命令
        :param command: 要执行的命令
        :return: 命令结果的Observable
        """
        pass
    
    @abstractmethod
    def get_all_command_metadata(self) -> Observable:
        """
        获取所有命令元数据
        :return: 命令元数据的Observable
        """
        pass
    
    @abstractmethod
    def get_command_metadata(self, command_id: str) -> Observable:
        """
        获取指定ID的命令元数据
        :param command_id: 命令ID
        :return: 命令元数据的Observable
        """
        pass


class CommandHandler(Generic[R, T], ABC):
    """命令处理器接口"""
    
    @abstractmethod
    def metadata(self) -> FunctionMetadata:
        """
        获取命令元数据
        :return: 命令元数据
        """
        pass
    
    @abstractmethod
    def execute(self, command: Dict[str, Any]) -> Observable:
        """
        执行命令
        :param command: 命令输入
        :return: 命令结果的Observable
        """
        pass


class SimpleCommandSupport(CommandSupport):
    """简单命令支持实现"""
    
    def __init__(self, handlers: Optional[List[CommandHandler]] = None):
        self.handlers: Dict[str, CommandHandler] = {}
        if handlers:
            for handler in handlers:
                self.handlers[handler.metadata().id] = handler
    
    def execute(self, command: Command[T]) -> Observable:
        """
        执行命令
        :param command: 要执行的命令
        :return: 命令结果的Observable
        """
        handler = self.handlers.get(command.id)
        
        if not handler:
            return rx.throw(Exception(f"不支持的命令: {command.id}"))
        
        if command.stream:
            return handler.execute({**command.inputs, "stream": command.stream})
        
        return handler.execute(command.inputs)
    
    def register_handler(self, handler: CommandHandler) -> 'SimpleCommandSupport':
        """
        注册命令处理器
        :param handler: 命令处理器
        :return: self
        """
        self.handlers[handler.metadata().id] = handler
        return self
    
    def unregister_handler(self, command_id: str) -> 'SimpleCommandSupport':
        """
        取消注册命令处理器
        :param command_id: 命令ID
        :return: self
        """
        if command_id in self.handlers:
            del self.handlers[command_id]
        return self
    
    def get_command_metadata(self, command_id: str) -> Observable:
        """
        获取指定ID的命令元数据
        :param command_id: 命令ID
        :return: 命令元数据的Observable
        """
        handler = self.handlers.get(command_id)
        
        def subscribe(observer, scheduler=None):
            if handler:
                observer.on_next(handler.metadata())
            observer.on_completed()
        
        return Observable(subscribe)
    
    def get_all_command_metadata(self) -> Observable:
        """
        获取所有命令元数据
        :return: 命令元数据的Observable
        """
        
        def subscribe(observer, scheduler=None):
            for handler in self.handlers.values():
                observer.on_next(handler.metadata())
            observer.on_completed()
        
        return Observable(subscribe)
    
    def has_command(self, command_id: str) -> bool:
        """
        检查命令是否存在
        :param command_id: 命令ID
        :return: 是否存在
        """
        return command_id in self.handlers 