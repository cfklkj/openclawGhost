"""
压缩工具模块
支持 ZIP 格式压缩
"""
import zipfile
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

class Compressor:
    """文件压缩/解压工具"""
    
    @staticmethod
    def compress(files: List[str], 
                 output_path: str, 
                 compress_type=zipfile.ZIP_DEFLATED) -> bool:
        """
        压缩文件到 ZIP
        
        Args:
            files: 要压缩的文件列表
            output_path: 输出的 ZIP 文件路径
            compress_type: 压缩类型
        
        Returns:
            是否成功
        """
        try:
            with zipfile.ZipFile(output_path, 'w', compress_type) as zf:
                for file_path in files:
                    if os.path.exists(file_path):
                        # 使用相对路径
                        arcname = os.path.basename(file_path)
                        zf.write(file_path, arcname)
            return True
        except Exception as e:
            print(f"压缩失败：{e}")
            return False
    
    @staticmethod
    def extract(zip_path: str, extract_to: str) -> bool:
        """
        解压 ZIP 文件
        
        Args:
            zip_path: ZIP 文件路径
            extract_to: 解压目标目录
        
        Returns:
            是否成功
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_to)
            return True
        except Exception as e:
            print(f"解压失败：{e}")
            return False
    
    @staticmethod
    def get_compressed_size(zip_path: str) -> int:
        """获取压缩文件大小"""
        try:
            return os.path.getsize(zip_path)
        except OSError:
            return 0
