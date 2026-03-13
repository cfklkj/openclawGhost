# -*- coding: utf-8 -*-
"""
CLI 测试脚本
验证第一阶段功能
"""
from openclawGhost.cli import cli
from click.testing import CliRunner

def test_version():
    """测试版本命令"""
    runner = CliRunner()
    result = runner.invoke(cli, ['version'])
    assert result.exit_code == 0
    print("[OK] version 命令测试通过")

def test_backup():
    """测试备份命令"""
    runner = CliRunner()
    result = runner.invoke(cli, ['backup', '--full', '--name', 'test-backup'])
    assert result.exit_code == 0
    print("[OK] backup 命令测试通过")

def test_snapshot_list():
    """测试快照列表"""
    runner = CliRunner()
    result = runner.invoke(cli, ['snapshot', 'list'])
    assert result.exit_code == 0
    print("[OK] snapshot list 命令测试通过")

def test_config_init():
    """测试配置初始化"""
    runner = CliRunner()
    result = runner.invoke(cli, ['config', 'init'])
    assert result.exit_code == 0
    print("[OK] config init 命令测试通过")

def test_restore():
    """测试还原命令"""
    runner = CliRunner()
    result = runner.invoke(cli, ['restore', 'snapshot_001', '--dry-run'])
    assert result.exit_code == 0
    print("[OK] restore 命令测试通过")

if __name__ == '__main__':
    print("开始测试 openclawGhost CLI...\n")
    test_version()
    test_backup()
    test_snapshot_list()
    test_config_init()
    test_restore()
    print("\n所有测试通过!")
