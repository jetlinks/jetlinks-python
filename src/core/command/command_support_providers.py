from typing import Dict, Any, Optional
import rx
from rx import Observable

from .command_support import CommandSupport
from .command import Command


class CommandSupportProviders:
    """命令支持提供者"""
    
    # 存储所有的命令支持
    _supports: Dict[str, CommandSupport] = {}
    
    @classmethod
    def register(cls, service_id: str, support: CommandSupport) -> None:
        """
        注册命令支持
        :param service_id: 服务ID
        :param support: 命令支持
        """
        cls._supports[service_id] = support
    
    @classmethod
    def get(cls, service_id: str) -> Optional[CommandSupport]:
        """
        获取命令支持
        :param service_id: 服务ID
        :return: 命令支持
        """
        return cls._supports.get(service_id)
    
    @classmethod
    def execute(cls, service_id: str, command_id: str, inputs: Dict[str, Any]) -> Observable:
        """
        执行命令
        :param service_id: 服务ID
        :param command_id: 命令ID
        :param inputs: 输入参数
        :return: 命令结果的Observable
        """
        support = cls.get(service_id)
        if not support:
            return rx.throw(Exception(f"不支持的服务: {service_id}"))
        
        command = Command(command_id, inputs)
        
        return support.execute(command)
    
    @classmethod
    def execute_stream(cls, service_id: str, command_id: str, inputs: Dict[str, Any], stream: Observable) -> Observable:
        """
        执行流式命令
        :param service_id: 服务ID
        :param command_id: 命令ID
        :param inputs: 输入参数
        :param stream: 输入流
        :return: 命令结果的Observable
        """
        support = cls.get(service_id)
        if not support:
            return rx.throw(Exception(f"不支持的服务: {service_id}"))
        
        command = Command(command_id, inputs)
        command.stream = stream
        
        return support.execute(command) 