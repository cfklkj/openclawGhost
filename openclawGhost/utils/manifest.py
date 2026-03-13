"""
文件清单生成器
扫描并生成 openclaw 项目文件清单
"""
import os
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class ManifestGenerator:
    """清单生成器"""
    
    def __init__(self, root_path: str):
        """
        初始化清单生成器
        
        Args:
            root_path: 项目根目录路径
        """
        self.root_path = Path(root_path)
        self.manifest = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "files": [],
            "directories": [],
            "total_files": 0,
            "total_size": 0
        }
    
    def scan(self, exclude_patterns: List[str] = None) -> Dict:
        """
        扫描项目生成清单
        
        Args:
            exclude_patterns: 排除模式列表
        
        Returns:
            清单字典
        """
        if not self.root_path.exists():
            raise FileNotFoundError(f"路径不存在：{self.root_path}")
        
        exclude_patterns = exclude_patterns or [
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '.git',
            '.gitignore',
            'node_modules',
            '*.log',
            '.openclawGhost',
            'backups',
            'metadata.json'
        ]
        
        total_size = 0
        file_count = 0
        
        for item in self.root_path.rglob('*'):
            # 检查排除规则
            if self._should_exclude(item, exclude_patterns):
                continue
            
            rel_path = str(item.relative_to(self.root_path))
            
            if item.is_file():
                try:
                    size = item.stat().st_size
                    mtime = datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    
                    self.manifest["files"].append({
                        "path": rel_path,
                        "size": size,
                        "mtime": mtime,
                        "type": self._get_file_type(rel_path)
                    })
                    
                    total_size += size
                    file_count += 1
                    
                except (PermissionError, OSError) as e:
                    print(f"警告：无法访问文件 {item}: {e}")
            
            elif item.is_dir():
                self.manifest["directories"].append(rel_path)
        
        self.manifest["total_files"] = file_count
        self.manifest["total_size"] = total_size
        
        return self.manifest
    
    def _should_exclude(self, item: Path, patterns: List[str]) -> bool:
        """检查是否应该排除"""
        item_str = str(item)
        item_name = item.name
        
        for pattern in patterns:
            if pattern.startswith('*') and item_name.endswith(pattern[1:]):
                return True
            if pattern.endswith('*') and item_name.startswith(pattern[:-1]):
                return True
            if pattern in item_str:
                return True
            if item_name == pattern:
                return True
        
        return False
    
    def _get_file_type(self, path: str) -> str:
        """根据扩展名判断文件类型"""
        ext = Path(path).suffix.lower()
        
        type_map = {
            '.py': 'python',
            '.md': 'markdown',
            '.json': 'json',
            '.txt': 'text',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.sh': 'shell',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.zip': 'archive',
            '.enc': 'encrypted',
        }
        
        return type_map.get(ext, 'unknown')
    
    def save(self, output_path: str = None) -> str:
        """
        保存清单到文件
        
        Args:
            output_path: 输出路径，默认为 root_path/.openclawGhost/manifest.json
        
        Returns:
            保存的文件路径
        """
        if output_path is None:
            output_dir = self.root_path / '.openclawGhost'
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / 'manifest.json'
        else:
            output_path = Path(output_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        
        print(f"清单已保存：{output_path}")
        return str(output_path)
    
    def print_summary(self):
        """打印清单摘要"""
        print("\n" + "="*60)
        print("openclaw 项目文件清单摘要")
        print("="*60)
        print(f"项目根目录：{self.root_path}")
        print(f"生成时间：{self.manifest['generated_at']}")
        print(f"文件总数：{self.manifest['total_files']}")
        print(f"目录总数：{len(self.manifest['directories'])}")
        print(f"总大小：{self._format_size(self.manifest['total_size'])}")
        
        # 按类型统计
        type_count = {}
        for file_info in self.manifest['files']:
            ftype = file_info.get('type', 'unknown')
            type_count[ftype] = type_count.get(ftype, 0) + 1
        
        print("\n文件类型分布:")
        for ftype, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ftype}: {count}")
        
        print("="*60)
    
    def _format_size(self, size: int) -> str:
        """格式化大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"


def generate_openclaw_manifest(root_path: str = None) -> ManifestGenerator:
    """
    生成 openclaw 项目清单
    
    Args:
        root_path: openclaw 项目根目录，默认为当前工作目录
    
    Returns:
        ManifestGenerator 实例
    """
    if root_path is None:
        root_path = Path.cwd()
    
    generator = ManifestGenerator(str(root_path))
    generator.scan()
    
    return generator


if __name__ == '__main__':
    # 示例：生成当前目录的清单
    import sys
    
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print(f"正在扫描：{root}")
    generator = generate_openclaw_manifest(root)
    generator.print_summary()
    generator.save()
