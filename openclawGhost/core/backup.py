"""
备份引擎
实现完整备份、增量备份、压缩、加密功能
支持基于清单的备份
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
from ..utils.manifest import ManifestGenerator

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
    manifest_path: Optional[str] = None  # 清单文件路径

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
               exclude_patterns: List[str] = None,
               manifest_path: str = None) -> Optional[BackupMetadata]:
        """
        执行备份
        
        Args:
            source_path: 源目录路径
            name: 备份名称
            backup_type: 备份类型 ('full' 或 'incremental')
            compress: 是否压缩
            encrypt: 是否加密
            exclude_patterns: 排除模式列表
            manifest_path: 清单文件路径（可选，如果提供则按清单备份）
        
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
        
        # 如果提供了清单文件，使用清单备份
        if manifest_path:
            return self._backup_from_manifest(
                manifest_path=manifest_path,
                name=name,
                backup_type=backup_type,
                compress=compress,
                encrypt=encrypt
            )
        
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
    
    def backup_from_manifest(self, manifest_path: str, **kwargs) -> Optional[BackupMetadata]:
        """
        从清单文件执行备份
        
        Args:
            manifest_path: 清单文件路径
            **kwargs: 传递给 backup 的参数
        
        Returns:
            BackupMetadata 对象或 None
        """
        return self.backup(
            source_path="",  # 清单模式不使用
            manifest_path=manifest_path,
            **kwargs
        )
    
    def _backup_from_manifest(self, manifest_path: str, **kwargs) -> Optional[BackupMetadata]:
        """从清单文件执行备份的内部方法"""
        print(f"使用清单文件：{manifest_path}")
        
        # 读取清单
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        root_path = Path(manifest_data.get('root_path', '.'))
        files = manifest_data.get('files', [])
        
        if not files:
            print("清单中没有文件")
            return None
        
        print(f"清单文件数：{len(files)}")
        print(f"项目根目录：{root_path}")
        
        # 生成备份 ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"backup_{timestamp}"
        name = kwargs.get('name') or timestamp
        
        # 创建备份目录
        backup_dir = self.backup_root / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制清单中的文件
        files_data = []
        total_size = 0
        file_hashes = {}
        
        for file_info in files:
            file_path = root_path / file_info['path']
            
            if not file_path.exists():
                print(f"警告：文件不存在 {file_path}")
                continue
            
            try:
                rel_path = file_info['path']
                dest_path = backup_dir / rel_path
                
                # 创建目标目录
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(str(file_path), str(dest_path))
                files_data.append(rel_path)
                total_size += file_path.stat().st_size
                
                # 计算哈希
                from .scanner import FileScanner
                file_hashes[rel_path] = FileScanner()._calculate_hash(file_path)
                
            except Exception as e:
                print(f"警告：复制文件失败 {file_path}: {e}")
        
        if not files_data:
            print("没有可备份的文件")
            shutil.rmtree(backup_dir, ignore_errors=True)
            return None
        
        # 压缩（如果需要）
        compressed = False
        if kwargs.get('compress') and files_data:
            print("正在压缩...")
            zip_path = backup_dir.with_suffix('.zip')
            if Compressor.compress(
                [str(backup_dir / f) for f in files_data],
                str(zip_path)
            ):
                shutil.rmtree(backup_dir)
                backup_dir = Path(str(backup_dir) + '.zip')
                compressed = True
                print(f"压缩完成：{zip_path}")
        
        # 加密（如果需要）
        encrypted = False
        if kwargs.get('encrypt'):
            print("正在加密...")
            encryptor = FileEncryptor()
            if compressed:
                enc_path = str(backup_dir) + '.enc'
                if encryptor.encrypt_file(str(backup_dir), enc_path):
                    backup_dir = Path(enc_path)
                    encrypted = True
                    encryptor.save_key(str(backup_dir) + '.key')
                    print(f"加密完成：{enc_path}")
        
        # 创建元数据
        metadata = BackupMetadata(
            id=backup_id,
            name=name,
            timestamp=timestamp,
            type=kwargs.get('backup_type', 'full'),
            source_path=str(root_path),
            backup_path=str(backup_dir),
            files_count=len(files_data),
            total_size=total_size,
            compressed=compressed,
            encrypted=encrypted,
            files_hash=file_hashes,
            manifest_path=manifest_path
        )
        
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
                base_backup_id=meta.get('base_backup_id'),
                manifest_path=meta.get('manifest_path')
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
