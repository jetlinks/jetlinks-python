from enum import Enum, auto
from typing import Dict, Any, List, Optional


class DataTypeId(str, Enum):
    """数据类型ID枚举"""
    INT = "int"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    BOOLEAN = "boolean"
    DATE = "date"
    FILE = "file"
    OBJECT = "object"
    ARRAY = "array"


class DataType:
    """数据类型基类"""
    
    def __init__(self, type_id: DataTypeId):
        self.id = type_id
        self.expands: Optional[Dict[str, Any]] = None
        
    def with_expands(self, expands: Dict[str, Any]) -> 'DataType':
        """设置扩展属性"""
        self.expands = expands
        return self


class ObjectType(DataType):
    """对象类型"""
    
    def __init__(self, properties: List['PropertyMetadata']):
        super().__init__(DataTypeId.OBJECT)
        self.properties = properties 