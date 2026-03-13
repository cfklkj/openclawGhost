"""
配置管理器
负责加载、保存和管理 openclawGhost 的配置
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "version": "1.0",
    "backup": {
        "default_path": "",
        "compress": True,
        "encrypt": False,
        "exclude_patterns": [
            "*.tmp",
            "*.log",
            "__pycache__",
            ".git"
        ]
    },
    "storage": {
        "type": "local",
        "path": ""
    },
    "schedule": {
        "enabled": False,
        "cron": "0 2 * * *"
    }
}

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # 默认配置文件路径
            app_dir = Path.home() / ".openclawGhost"
            self.config_path = app_dir / "config.json"
        
        self._config: Dict[str, Any] = {}
    
    def load(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告：配置文件加载失败 {e}, 使用默认配置")
                self._config = DEFAULT_CONFIG.copy()
        else:
            self._config = DEFAULT_CONFIG.copy()
        
        return self._config
    
    def save(self) -> bool:
        """保存配置"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"错误：保存配置失败 {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def init(self) -> Dict[str, Any]:
        """初始化配置"""
        self._config = DEFAULT_CONFIG.copy()
        self.save()
        return self._config
