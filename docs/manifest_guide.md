# openclaw 文件清单备份指南

## 概述

openclawGhost 支持基于**文件清单（Manifest）**进行备份，适用于：
- 精确控制备份范围
- 选择性备份特定文件
- 生成项目文件清单用于审计
- 基于清单还原特定文件

## 快速开始

### 1. 生成文件清单

```bash
# 为当前项目生成清单
openclawGhost manifest .

# 指定输出路径
openclawGhost manifest . --output my_manifest.json

# 排除特定文件
openclawGhost manifest . --exclude "*.log" --exclude "*.tmp"
```

### 2. 基于清单备份

```bash
# 使用清单文件备份
openclawGhost backup --manifest .openclawGhost/manifest.json

# 压缩备份
openclawGhost backup --manifest .openclawGhost/manifest.json --compress

# 加密备份
openclawGhost backup --manifest .openclawGhost/manifest.json --compress --encrypt
```

## 清单文件结构

```json
{
  "version": "1.0",
  "generated_at": "2026-03-13T11:06:23.340828",
  "root_path": "H:\\path\\to\\project",
  "files": [
    {
      "path": "README.md",
      "size": 2188,
      "mtime": "2026-03-13T08:53:00",
      "type": "markdown"
    },
    {
      "path": "src/main.py",
      "size": 1024,
      "mtime": "2026-03-13T10:00:00",
      "type": "python"
    }
  ],
  "directories": [
    "src",
    "docs",
    "tests"
  ],
  "total_files": 33,
  "total_size": 83030
}
```

## 清单字段说明

### 顶层字段
- `version`: 清单格式版本
- `generated_at`: 生成时间（ISO 8601）
- `root_path`: 项目根目录
- `files`: 文件列表
- `directories`: 目录列表
- `total_files`: 文件总数
- `total_size`: 总大小（字节）

### 文件信息字段
- `path`: 相对路径
- `size`: 文件大小（字节）
- `mtime`: 修改时间
- `type`: 文件类型（python/markdown/json/text/shell/unknown）

## 使用场景

### 场景 1: 项目完整备份

```bash
# 生成清单
openclawGhost manifest /path/to/openclaw

# 基于清单备份
openclawGhost backup --manifest .openclawGhost/manifest.json --compress --name "full-backup"
```

### 场景 2: 选择性备份

创建自定义清单文件：

```json
{
  "version": "1.0",
  "root_path": "/path/to/openclaw",
  "files": [
    {"path": "config.json", "size": 1024, "mtime": "...", "type": "json"},
    {"path": "agents.json", "size": 2048, "mtime": "...", "type": "json"}
  ],
  "directories": [],
  "total_files": 2,
  "total_size": 3072
}
```

```bash
openclawGhost backup --manifest custom_manifest.json --compress
```

### 场景 3: 排除临时文件

```bash
# 生成清单时排除日志和临时文件
openclawGhost manifest . --exclude "*.log" --exclude "*.tmp" --exclude "__pycache__"

# 基于清单备份
openclawGhost backup --manifest .openclawGhost/manifest.json
```

### 场景 4: 增量备份

```bash
# 第一次：生成清单并完整备份
openclawGhost manifest .
openclawGhost backup --manifest .openclawGhost/manifest.json --name "base"

# 修改文件后：重新生成清单
openclawGhost manifest .

# 增量备份
openclawGhost backup --manifest .openclawGhost/manifest.json --incremental --name "incremental"
```

## Python API 使用

### 生成清单

```python
from openclawGhost.utils.manifest import ManifestGenerator

generator = ManifestGenerator('/path/to/project')
generator.scan(exclude_patterns=['*.log', '*.tmp'])
generator.print_summary()
generator.save('manifest.json')
```

### 基于清单备份

```python
from openclawGhost.core.backup import BackupEngine

engine = BackupEngine()
metadata = engine.backup_from_manifest(
    manifest_path='manifest.json',
    name='my-backup',
    compress=True,
    encrypt=False
)

print(f"备份成功！ID: {metadata.id}")
print(f"文件数：{metadata.files_count}")
```

### 自定义清单

```python
import json
from pathlib import Path

# 创建自定义清单
manifest = {
    "version": "1.0",
    "root_path": str(Path.cwd()),
    "files": [],
    "directories": [],
    "total_files": 0,
    "total_size": 0
}

# 添加特定文件
files_to_backup = ['config.json', 'agents.json', 'models.json']
for file_name in files_to_backup:
    file_path = Path(file_name)
    if file_path.exists():
        manifest["files"].append({
            "path": file_name,
            "size": file_path.stat().st_size,
            "mtime": "...",
            "type": "json"
        })

manifest["total_files"] = len(manifest["files"])
manifest["total_size"] = sum(f["size"] for f in manifest["files"])

# 保存清单
with open('custom_manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)

# 执行备份
engine.backup_from_manifest('custom_manifest.json')
```

## 清单管理命令

```bash
# 查看清单
cat .openclawGhost/manifest.json

# 查看备份列表（包含清单信息）
openclawGhost snapshot list

# 查看特定备份的清单路径
openclawGhost snapshot show backup_20260313_110731
```

## openclaw 项目清单示例

为 openclaw 项目生成清单：

```bash
cd /path/to/openclaw
openclawGhost manifest . --exclude "*.log" --exclude "node_modules"
openclawGhost backup --manifest .openclawGhost/manifest.json --compress --name "openclaw-backup"
```

生成的清单将包含：
- Python 源文件（*.py）
- 配置文件（*.json, *.yaml）
- 文档（*.md）
- 脚本（*.sh, *.ps1）

## 清单优势

1. **精确控制**: 明确指定要备份的文件
2. **审计追踪**: 记录文件元数据（大小、修改时间）
3. **选择性备份**: 可以手动编辑清单选择特定文件
4. **版本对比**: 通过清单对比文件变更
5. **增量备份**: 基于清单对比实现增量备份

## 注意事项

- 清单文件默认保存在 `.openclawGhost/manifest.json`
- 清单中的路径是相对于 `root_path` 的相对路径
- 修改清单后需重新生成才能反映最新文件状态
- 清单备份模式会忽略 `source_path` 参数，使用清单中的 `root_path`

## 测试清单备份

```bash
# 运行清单备份测试
python test_manifest.py
```

测试内容：
- 生成项目清单
- 基于清单完整备份
- 选择性清单备份
- 排除规则测试

---

**相关文档**:
- [第二阶段总结](phase2_summary.md)
- [快速开始](quickstart.md)
