'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2025-02-10 15:32:06
LastEditTime: 2025-02-10 15:32:11
FilePath: /tcl-check-of-dirty-api/src/config_manager.py
'''
import os
import yaml
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.config_cache = {}
        
    def get_config(self, factory: str, product: str) -> Dict[Any, Any]:
        """
        按优先级获取配置：
        1. 工厂特定产品配置 (factories/dw1/coolant.yaml)
        2. 工厂通用配置 (factories/dw1/config.yaml)
        3. 产品通用配置 (products/coolant.yaml)
        4. 默认配置 (default.yaml)
        """
        config = {}
        
        # 加载默认配置
        default_config = self._load_yaml('default.yaml')
        config.update(default_config or {})
        
        # 加载产品通用配置
        product_config = self._load_yaml(f'products/{product}.yaml')
        config.update(product_config or {})
        
        # 加载工厂通用配置
        factory_config = self._load_yaml(f'factories/{factory}/config.yaml')
        config.update(factory_config or {})
        
        # 加载工厂特定产品配置
        factory_product_config = self._load_yaml(f'factories/{factory}/{product}.yaml')
        config.update(factory_product_config or {})
        
        return config
    
    def _load_yaml(self, relative_path: str) -> Dict[Any, Any]:
        """加载YAML文件，如果文件不存在返回None"""
        full_path = os.path.join(self.config_dir, relative_path)
        
        if full_path in self.config_cache:
            return self.config_cache[full_path]
            
        if not os.path.exists(full_path):
            return None
            
        with open(full_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.config_cache[full_path] = config
            return config 