# openclawGhost

> OpenClaw 轻量级备份还原工具

## 项目简介

openclawGhost 是 Ghost 系统的迷你版本，专门为 openclaw 应用设计的轻量级备份还原工具。提供一键备份/还原的便捷体验。

## 核心特性

- ✅ **简单**: 命令行一键操作，无需复杂配置
- ✅ **可靠**: 保证备份数据的完整性和一致性
- ✅ **快速**: 增量备份机制，节省时间和空间
- ✅ **安全**: 备份文件加密存储

## 快速开始

### 安装

```bash
# 从源码安装
cd openclawGhost
pip install -e .

# 或使用 pip 安装
pip install openclawghost
```

### 使用方法

```bash
# 初始化配置
openclawGhost config init

# 创建完整备份
openclawGhost backup --full --name "pre-update-backup"

# 查看备份列表
openclawGhost snapshot list

# 还原备份
openclawGhost restore <SNAPSHOT_ID>
```

## 命令行接口

### 备份命令

```bash
openclawGhost backup [OPTIONS]
  --full          执行完整备份
  --incremental   执行增量备份
  --name NAME     指定备份名称
  --encrypt       启用加密
  --compress      启用压缩
  --exclude       排除文件模式
```

### 还原命令

```bash
openclawGhost restore [SNAPSHOT_ID] [OPTIONS]
  --target PATH   还原到指定路径
  --dry-run       预演模式
  --force         强制覆盖
```

### 快照管理

```bash
openclawGhost snapshot list          # 查看快照列表
openclawGhost snapshot show [ID]     # 显示快照详情
openclawGhost snapshot delete [ID]   # 删除快照
openclawGhost snapshot compare [ID1] [ID2]  # 比较快照
```

### 配置管理

```bash
openclawGhost config init            # 初始化配置
openclawGhost config show            # 显示配置
openclawGhost config set KEY VALUE   # 设置配置项
```

## 开发进度

- [x] 项目结构搭建
- [x] CLI 命令行框架
- [x] 配置管理模块
- [x] 日志系统集成
- [ ] 备份功能实现
- [ ] 还原功能实现
- [ ] 快照管理
- [ ] 加密压缩

## 技术栈

- **语言**: Python 3.8+
- **CLI**: Click
- **加密**: Cryptography
- **压缩**: 待实现

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
