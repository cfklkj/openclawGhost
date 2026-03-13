# 快速开始指南

## 安装

```bash
pip install openclawghost
```

## 初始化

```bash
openclawGhost config init
```

## 备份

```bash
# 完整备份
openclawGhost backup --full --name "my-backup"

# 增量备份
openclawGhost backup --incremental
```

## 还原

```bash
# 查看快照列表
openclawGhost snapshot list

# 还原指定快照
openclawGhost restore <SNAPSHOT_ID>
```

## 配置

```bash
# 查看配置
openclawGhost config show

# 设置配置项
openclawGhost config set backup.compress true
```
