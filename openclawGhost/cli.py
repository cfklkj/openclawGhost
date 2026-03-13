"""
CLI 命令行入口
openclawGhost 命令行工具主入口
"""
import click
import sys
from pathlib import Path
from . import __version__
from .core.backup import BackupEngine
from .core.scanner import FileScanner

@click.group()
@click.version_option(version=__version__)
def cli():
    """openclawGhost - OpenClaw 轻量级备份还原工具"""
    pass

@cli.command()
def version():
    """显示版本信息"""
    click.echo(f"openclawGhost version {__version__}")

@cli.command()
@click.option('--full', is_flag=True, help='执行完整备份')
@click.option('--incremental', is_flag=True, help='执行增量备份')
@click.option('--name', type=str, help='指定备份名称')
@click.option('--encrypt', is_flag=True, help='启用加密')
@click.option('--compress', is_flag=True, help='启用压缩')
@click.option('--exclude', type=str, multiple=True, help='排除文件模式')
@click.argument('source', default='.')
def backup(full, incremental, name, encrypt, compress, exclude, source):
    """
    执行备份操作
    
    SOURCE: 要备份的源目录路径（默认为当前目录）
    """
    backup_type = "full" if full else "incremental" if incremental else "full"
    
    # 验证源路径
    source_path = Path(source).resolve()
    if not source_path.exists():
        click.echo(f"错误：源路径不存在：{source_path}")
        return
    
    # 创建备份引擎
    engine = BackupEngine()
    
    # 执行备份
    metadata = engine.backup(
        source_path=str(source_path),
        name=name,
        backup_type=backup_type,
        compress=compress,
        encrypt=encrypt,
        exclude_patterns=list(exclude) if exclude else None
    )
    
    if metadata:
        click.echo(f"\n备份成功！ID: {metadata.id}")
    else:
        click.echo("备份失败")

@cli.command()
@click.argument('snapshot_id')
@click.option('--target', type=str, help='还原到指定路径')
@click.option('--dry-run', is_flag=True, help='预演模式')
@click.option('--force', is_flag=True, help='强制覆盖')
def restore(snapshot_id, target, dry_run, force):
    """还原指定快照"""
    click.echo(f"准备还原快照：{snapshot_id}")
    if target:
        click.echo(f"目标路径：{target}")
    if dry_run:
        click.echo("模式：预演")
    if force:
        click.echo("警告：强制覆盖已启用")
    click.echo("还原功能待实现")

@cli.group()
def snapshot():
    """快照管理"""
    pass

@snapshot.command()
def list():
    """查看所有备份版本"""
    from pathlib import Path
    import json
    
    metadata_file = Path.home() / ".openclawGhost" / "backups" / "metadata.json"
    
    if not metadata_file.exists():
        click.echo("快照列表:")
        click.echo("  暂无快照")
        return
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        click.echo("快照列表:")
        click.echo("-" * 60)
        
        for backup_id, meta in data.items():
            click.echo(f"ID: {backup_id}")
            click.echo(f"  名称：{meta.get('name', 'N/A')}")
            click.echo(f"  时间：{meta.get('timestamp', 'N/A')}")
            click.echo(f"  类型：{meta.get('type', 'N/A')}")
            click.echo(f"  文件数：{meta.get('files_count', 0)}")
            click.echo(f"  大小：{meta.get('total_size', 0)} bytes")
            click.echo(f"  压缩：{'是' if meta.get('compressed') else '否'}")
            click.echo(f"  加密：{'是' if meta.get('encrypted') else '否'}")
            click.echo()
        
        click.echo("-" * 60)
        click.echo(f"共 {len(data)} 个快照")
        
    except Exception as e:
        click.echo(f"读取快照列表失败：{e}")

@snapshot.command()
@click.argument('snapshot_id')
def show(snapshot_id):
    """显示快照详情"""
    click.echo(f"快照 {snapshot_id} 详情:")
    click.echo("快照详情功能待实现")

@snapshot.command()
@click.argument('snapshot_id')
def delete(snapshot_id):
    """删除快照"""
    click.echo(f"删除快照 {snapshot_id}")
    click.echo("快照删除功能待实现")

@snapshot.command()
@click.argument('id1')
@click.argument('id2')
def compare(id1, id2):
    """比较两个快照"""
    click.echo(f"比较 {id1} 和 {id2}")
    click.echo("快照对比功能待实现")

@cli.group()
def config():
    """配置管理"""
    pass

@config.command()
def init():
    """初始化配置"""
    click.echo("初始化配置...")
    click.echo("配置初始化功能待实现")

@config.command()
def show():
    """显示当前配置"""
    click.echo("当前配置:")
    click.echo("配置显示功能待实现")

@config.command(name='set')
@click.argument('key')
@click.argument('value')
def set_config(key, value):
    """设置配置项"""
    click.echo(f"设置 {key} = {value}")
    click.echo("配置设置功能待实现")

if __name__ == '__main__':
    cli()
