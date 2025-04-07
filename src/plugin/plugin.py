from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

import rx

from ..core.monitor import Monitor,Logger
from ..core.command.command_support import SimpleCommandSupport,CommandSupport

class PluginType:
    """插件类型，用于描述插件的类型，如设备接入等"""
    
    def __init__(self, type_id: str, name: str):
        """
        初始化插件类型
        
        Args:
            type_id: 插件类型ID
            name: 插件类型名称
        """
        self.id = type_id
        self.name = name
        
    def __str__(self) -> str:
        return f"PluginType(id={self.id}, name={self.name})"
        
    def __repr__(self) -> str:
        return self.__str__()


class PluginContext(ABC):
    """
    插件上下文接口，提供插件运行所需的环境和服务
    由调用者实现并传入到插件中
    """
    
    @abstractmethod
    def monitor(self) -> Monitor:
        """
        获取监控实例
        
        Returns:
            Monitor: 监控实例
            
        Raises:
            Exception: 当监控实例不可用时抛出异常
        """
        pass
    
    @abstractmethod
    def service(self, service_id: str) -> CommandSupport:
        """
        获取指定ID的服务
        
        Args:
            service_id: 服务ID
            
        Returns:
            CommandSupport: 命令支持服务
            
        Raises:
            Exception: 当服务不存在时抛出异常
        """
        pass
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """
        获取配置信息
        
        Returns:
            Dict[str, Any]: 配置信息
        """
        pass


class Plugin(SimpleCommandSupport, ABC):
    """插件实例，运行中的插件"""
    
    def __init__(self, context: PluginContext):
        """
        初始化插件
        
        Args:
            context: 插件上下文
        """
        super().__init__()
        self.context = context
        
    def start(self) -> None:
        """启动插件"""
        pass
        
    def stop(self) -> None:
        """停止插件"""
        pass



