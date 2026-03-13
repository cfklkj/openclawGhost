# -*- coding: utf-8 -*-
"""
备份功能测试脚本
"""
import os
import tempfile
import shutil
from pathlib import Path

def create_test_files():
    """创建测试文件"""
    test_dir = Path(tempfile.mkdtemp())
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建一些测试文件
    (test_dir / "file1.txt").write_text("Hello, World!")
    (test_dir / "file2.txt").write_text("Test backup functionality")
    
    # 创建子目录
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Nested file")
    
    print(f"测试目录：{test_dir}")
    print(f"文件列表：")
    for f in test_dir.rglob("*"):
        if f.is_file():
            print(f"  {f.relative_to(test_dir)}")
    
    return test_dir

def test_full_backup():
    """测试完整备份"""
    from openclawGhost.core.backup import BackupEngine
    
    # 创建测试文件
    test_dir = create_test_files()
    
    try:
        # 创建备份引擎
        engine = BackupEngine()
        
        # 执行完整备份
        print("\n" + "="*60)
        print("测试完整备份...")
        print("="*60)
        
        metadata = engine.backup(
            source_path=str(test_dir),
            name="test-full-backup",
            backup_type="full",
            compress=False,
            encrypt=False
        )
        
        if metadata:
            print("\n[OK] 完整备份测试成功!")
            print(f"  备份ID: {metadata.id}")
            print(f"  文件数: {metadata.files_count}")
            print(f"  总大小: {metadata.total_size} bytes")
            return True
        else:
            print("\n[FAIL] 完整备份测试失败!")
            return False
    
    finally:
        # 清理测试目录
        shutil.rmtree(test_dir, ignore_errors=True)

def test_compressed_backup():
    """测试压缩备份"""
    from openclawGhost.core.backup import BackupEngine
    
    test_dir = create_test_files()
    
    try:
        engine = BackupEngine()
        
        print("\n" + "="*60)
        print("测试压缩备份...")
        print("="*60)
        
        metadata = engine.backup(
            source_path=str(test_dir),
            name="test-compressed-backup",
            backup_type="full",
            compress=True,
            encrypt=False
        )
        
        if metadata and metadata.compressed:
            print("\n[OK] 压缩备份测试成功!")
            return True
        else:
            print("\n[FAIL] 压缩备份测试失败!")
            return False
    
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

def test_encrypted_backup():
    """测试加密备份"""
    from openclawGhost.core.backup import BackupEngine
    
    test_dir = create_test_files()
    
    try:
        engine = BackupEngine()
        
        print("\n" + "="*60)
        print("测试加密备份...")
        print("="*60)
        
        metadata = engine.backup(
            source_path=str(test_dir),
            name="test-encrypted-backup",
            backup_type="full",
            compress=True,
            encrypt=True
        )
        
        if metadata and metadata.encrypted:
            print("\n[OK] 加密备份测试成功!")
            return True
        else:
            print("\n[FAIL] 加密备份测试失败!")
            return False
    
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == '__main__':
    print("开始测试 openclawGhost 备份功能...\n")
    
    results = []
    results.append(("完整备份", test_full_backup()))
    results.append(("压缩备份", test_compressed_backup()))
    results.append(("加密备份", test_encrypted_backup()))
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\n总计: {passed}/{len(results)} 测试通过")
