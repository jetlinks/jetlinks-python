from typing import List, Optional, Union, Dict, Any
from .property_metadata import PropertyMetadata
from .data_type import DataType, DataTypeId


class FunctionMetadata:
    """函数元数据"""
    
    def __init__(self, func_id: str, name: str, inputs: List[PropertyMetadata], output: Union[DataType, DataTypeId]):
        self.id = func_id
        self.name = name
        self.description: Optional[str] = None
        self.inputs = inputs
        self.output = output
        
    def with_description(self, description: str) -> 'FunctionMetadata':
        """设置描述信息"""
        self.description = description
        return self


class SimpleFunctionMetadata(FunctionMetadata):
    """简化版函数元数据，用于命令支持"""
    
    def __init__(self, func_id: str = None, name: str = None, description: str = None):
        """
        初始化
        
        :param func_id: 函数ID
        :param name: 函数名称
        :param description: 函数描述
        """
        # 使用空列表初始化inputs
        super().__init__(func_id or "", name or "", [], None)
        
        if description:
            self.description = description
        
        # 添加扩展属性
        self.expands: Dict[str, Any] = {}
    
    def set_id(self, func_id: str):
        """设置函数ID"""
        self.id = func_id
        return self
    
    def set_name(self, name: str):
        """设置函数名称"""
        self.name = name
        return self
    
    def set_description(self, description: str):
        """设置函数描述"""
        self.description = description
        return self
    
    def set_inputs(self, inputs: List[PropertyMetadata]):
        """设置输入参数"""
        self.inputs = inputs
        return self
    
    def set_output(self, output: Union[DataType, DataTypeId]):
        """设置输出类型"""
        self.output = output
        return self
    
    def expand(self, key: str, value: Any):
        """添加扩展属性"""
        self.expands[key] = value
        return self 