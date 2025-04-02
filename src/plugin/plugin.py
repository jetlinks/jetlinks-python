from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

from ..core.monitor import Monitor,Logger
from ..core.command.command_support import SimpleCommandSupport

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


class Plugin(SimpleCommandSupport, ABC):
    """插件实例，运行中的插件"""
    
    def __init__(self, context: PluginContext):
        """
        初始化插件
        
        Args:
            context: 插件上下文
        """
        self.context = context

        
    def start(self) -> None:
        """启动插件"""
        pass
        
    def stop(self) -> None:
        """停止插件"""
        pass


