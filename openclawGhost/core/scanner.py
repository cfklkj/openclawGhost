"""
文件扫描和差异检测模块
负责扫描文件、计算哈希值、检测变更
"""
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileInfo:
    """文件信息"""
    path: str
    size: int
    mtime: float
    hash: str

class FileScanner:
    """文件扫描器"""
    
    def __init__(self, exclude_patterns: List[str] = None):
        self.exclude_patterns = exclude_patterns or []
    
    def scan(self, root_path: str) -> Dict[str, FileInfo]:
        """
        扫描目录下的所有文件
        
        Args:
            root_path: 根目录路径
        
        Returns:
            文件路径到 FileInfo 的映射
        """
        files = {}
        root = Path(root_path)
        
        if not root.exists():
            return files
        
        for file_path in root.rglob('*'):
            # 跳过目录
            if file_path.is_dir():
                continue
            
            # 检查排除规则
            if self._should_exclude(file_path):
                continue
            
            try:
                stat = file_path.stat()
                file_hash = self._calculate_hash(file_path)
                
                files[str(file_path)] = FileInfo(
                    path=str(file_path),
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                    hash=file_hash
                )
            except (PermissionError, OSError) as e:
                print(f"警告：无法访问文件 {file_path}: {e}")
        
        return files
    
    def _should_exclude(self, file_path: Path) -> bool:
        """检查文件是否应该被排除"""
        file_name = file_path.name
        file_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            # 简单通配符匹配
            if pattern.startswith('*') and file_name.endswith(pattern[1:]):
                return True
            if pattern.endswith('*') and file_name.startswith(pattern[:-1]):
                return True
            if pattern in file_str:
                return True
            if file_name == pattern:
                return True
        
        return False
    
    def _calculate_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """计算文件 SHA-256 哈希值"""
        hasher = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError):
            return ""
    
    def detect_changes(self, 
                      old_files: Dict[str, FileInfo],
                      new_files: Dict[str, FileInfo]) -> Tuple[List[str], List[str], List[str]]:
        """
        检测文件变化
        
        Args:
            old_files: 上次的文件信息
            new_files: 当前的文件信息
        
        Returns:
            (added_paths, modified_paths, deleted_paths)
        """
        old_set = set(old_files.keys())
        new_set = set(new_files.keys())
        
        # 新增的文件
        added = list(new_set - old_set)
        
        # 删除的文件
        deleted = list(old_set - new_set)
        
        # 可能修改的文件（通过哈希对比）
        modified = []
        common = old_set & new_set
        for path in common:
            if old_files[path].hash != new_files[path].hash:
                modified.append(path)
        
        return added, modified, deleted
