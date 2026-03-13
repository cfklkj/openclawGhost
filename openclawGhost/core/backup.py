"""
备份引擎
实现完整备份、增量备份、压缩、加密功能
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from .scanner import FileScanner, FileInfo
from ..utils.compress import Compressor
from ..storage.crypto import FileEncryptor, generate_key

@dataclass
class BackupMetadata:
    """备份元数据"""
    id: str
    name: str
    timestamp: str
    type: str  # 'full' or 'incremental'
    source_path: str
    backup_path: str
    files_count: int
    total_size: int
    compressed: bool
    encrypted: bool
    files_hash: Dict[str, str]  # 文件路径 -> 哈希值
    base_backup_id: Optional[str] = None  # 增量备份的基础备份 ID

class BackupEngine:
    """备份引擎"""
    
    def __init__(self, backup_root: str = None):
        """
        初始化备份引擎
        
        Args:
            backup_root: 备份存储根目录
        """
        self.backup_root = backup_root or Path.home() / ".openclawGhost" / "backups"
        self.backup_root = Path(self.backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        self.scanner = FileScanner()
        self.metadata_file = self.backup_root / "metadata.json"
    
    def backup(self,
               source_path: str,
               name: str = None,
               backup_type: str = 'full',
               compress: bool = False,
               encrypt: bool = False,
               exclude_patterns: List[str] = None) -> Optional[BackupMetadata]:
        """
        执行备份
        
        Args:
            source_path: 源目录路径
            name: 备份名称
            backup_type: 备份类型 ('full' 或 'incremental')
            compress: 是否压缩
            encrypt: 是否加密
            exclude_patterns: 排除模式列表
        
        Returns:
            BackupMetadata 对象或 None
        """
        # 生成备份 ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"backup_{timestamp}"
        name = name or timestamp
        
        # 创建备份目录
        backup_dir = self.backup_root / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"开始备份：{name}")
        print(f"备份类型：{backup_type}")
        print(f"源路径：{source_path}")
        
        # 扫描文件
        self.scanner.exclude_patterns = exclude_patterns or []
        current_files = self.scanner.scan(source_path)
        
        if not current_files:
            print("警告：未找到任何文件")
            return None
        
        # 如果是增量备份，获取上次的文件哈希
        base_backup_id = None
        if backup_type == 'incremental':
            last_metadata = self._get_last_backup()
            if last_metadata:
                base_backup_id = last_metadata.id
                print(f"基于备份：{base_backup_id}")
        
        print(f"扫描到 {len(current_files)} 个文件")
        
        # 复制文件到备份目录（增量备份只复制变化的文件）
        files_data = []
        total_size = 0
        
        for file_path, file_info in current_files.items():
            try:
                # 计算相对路径
                rel_path = os.path.relpath(file_path, source_path)
                
                # 检查是否需要备份此文件
                if backup_type == 'incremental':
                    last_meta = self._get_last_backup()
                    if last_meta and rel_path in last_meta.files_hash:
                        # 文件存在且哈希相同，跳过
                        if file_info.hash == last_meta.files_hash[rel_path]:
                            continue
                
                dest_path = backup_dir / rel_path
                
                # 创建目标目录
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(file_path, dest_path)
                files_data.append(rel_path)
                total_size += file_info.size
                
            except Exception as e:
                print(f"警告：复制文件失败 {file_path}: {e}")
        
        if not files_data:
            print("没有需要备份的变更文件")
            # 清理空目录
            shutil.rmtree(backup_dir, ignore_errors=True)
            return None
        
        # 压缩（如果需要）
        compressed = False
        if compress and files_data:
            print("正在压缩...")
            zip_path = backup_dir.with_suffix('.zip')
            if Compressor.compress(
                [str(backup_dir / f) for f in files_data],
                str(zip_path)
            ):
                # 删除原始目录，保留 ZIP
                shutil.rmtree(backup_dir)
                backup_dir = Path(str(backup_dir) + '.zip')
                compressed = True
                print(f"压缩完成：{zip_path}")
        
        # 加密（如果需要）
        encrypted = False
        if encrypt:
            print("正在加密...")
            encryptor = FileEncryptor()
            if compressed:
                # 加密 ZIP 文件
                enc_path = str(backup_dir) + '.enc'
                if encryptor.encrypt_file(str(backup_dir), enc_path):
                    backup_dir = Path(enc_path)
                    encrypted = True
                    # 保存密钥
                    key_path = str(backup_dir) + '.key'
                    encryptor.save_key(key_path)
                    print(f"加密完成：{enc_path}")
            else:
                # 加密整个目录（先压缩再加密）
                zip_path = str(backup_dir) + '.zip'
                if Compressor.compress(
                    [str(backup_dir / f) for f in files_data],
                    zip_path
                ):
                    enc_path = zip_path + '.enc'
                    if encryptor.encrypt_file(zip_path, enc_path):
                        shutil.rmtree(backup_dir)
                        os.remove(zip_path)
                        backup_dir = Path(enc_path)
                        encrypted = True
                        encryptor.save_key(str(backup_dir) + '.key')
                        print(f"加密完成：{enc_path}")
        
        # 创建元数据
        metadata = BackupMetadata(
            id=backup_id,
            name=name,
            timestamp=timestamp,
            type=backup_type,
            source_path=str(source_path),
            backup_path=str(backup_dir),
            files_count=len(files_data),
            total_size=total_size,
            compressed=compressed,
            encrypted=encrypted,
            files_hash={k: v.hash for k, v in current_files.items()},
            base_backup_id=base_backup_id
        )
        
        # 保存元数据
        self._save_metadata(metadata)
        
        print(f"\n备份完成!")
        print(f"备份 ID: {backup_id}")
        print(f"文件数：{len(files_data)}")
        print(f"总大小：{self._format_size(total_size)}")
        print(f"压缩：{'是' if compressed else '否'}")
        print(f"加密：{'是' if encrypted else '否'}")
        
        return metadata
    
    def _get_last_backup(self) -> Optional[BackupMetadata]:
        """获取上一次备份的元数据"""
        if not self.metadata_file.exists():
            return None
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                return None
            
            # 获取最后一个备份
            last_id = list(data.keys())[-1]
            meta = data[last_id]
            
            return BackupMetadata(
                id=meta['id'],
                name=meta['name'],
                timestamp=meta['timestamp'],
                type=meta['type'],
                source_path=meta['source_path'],
                backup_path=meta['backup_path'],
                files_count=meta['files_count'],
                total_size=meta['total_size'],
                compressed=meta['compressed'],
                encrypted=meta['encrypted'],
                files_hash=meta['files_hash'],
                base_backup_id=meta.get('base_backup_id')
            )
        except Exception as e:
            print(f"读取上次备份失败：{e}")
            return None
    
    def _save_metadata(self, metadata: BackupMetadata):
        """保存元数据到 JSON"""
        data = {}
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {}
        
        data[metadata.id] = asdict(metadata)
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
