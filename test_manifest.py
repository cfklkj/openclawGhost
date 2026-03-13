# -*- coding: utf-8 -*-
"""
清单备份测试脚本
演示如何生成清单并基于清单备份
"""
import json
from pathlib import Path
from openclawGhost.utils.manifest import ManifestGenerator
from openclawGhost.core.backup import BackupEngine

def test_manifest_backup():
    """测试清单备份流程"""
    
    # 步骤 1: 生成项目清单
    print("="*60)
    print("步骤 1: 生成项目清单")
    print("="*60)
    
    project_path = Path.cwd()
    print(f"项目路径：{project_path}")
    
    generator = ManifestGenerator(str(project_path))
    generator.scan()
    generator.print_summary()
    
    # 保存清单
    manifest_file = generator.save()
    
    # 步骤 2: 查看清单内容
    print("\n" + "="*60)
    print("步骤 2: 查看清单内容")
    print("="*60)
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest_data = json.load(f)
    
    print(f"清单版本：{manifest_data['version']}")
    print(f"生成时间：{manifest_data['generated_at']}")
    print(f"根路径：{manifest_data['root_path']}")
    print(f"文件总数：{manifest_data['total_files']}")
    print(f"总大小：{manifest_data['total_size']} bytes")
    
    print(f"\n前 5 个文件:")
    for file_info in manifest_data['files'][:5]:
        print(f"  - {file_info['path']} ({file_info['size']} bytes)")
    
    # 步骤 3: 基于清单执行备份
    print("\n" + "="*60)
    print("步骤 3: 基于清单执行备份")
    print("="*60)
    
    engine = BackupEngine()
    
    # 完整备份（压缩）
    metadata = engine.backup_from_manifest(
        manifest_path=manifest_file,
        name="manifest-test-backup",
        backup_type="full",
        compress=True,
        encrypt=False
    )
    
    if metadata:
        print("\n" + "="*60)
        print("备份成功!")
        print("="*60)
        print(f"备份 ID: {metadata.id}")
        print(f"文件数：{metadata.files_count}")
        print(f"总大小：{metadata.total_size} bytes")
        print(f"压缩：{'是' if metadata.compressed else '否'}")
        print(f"加密：{'是' if metadata.encrypted else '否'}")
        print(f"清单路径：{metadata.manifest_path}")
        
        return True
    else:
        print("\n备份失败")
        return False

def test_selective_backup():
    """测试选择性清单备份"""
    import tempfile
    import shutil
    
    print("\n" + "="*60)
    print("测试选择性清单备份")
    print("="*60)
    
    # 创建临时项目
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # 创建一些文件
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").write_text("print('Hello')")
        (temp_dir / "src" / "utils.py").write_text("def helper(): pass")
        (temp_dir / "README.md").write_text("# Project")
        (temp_dir / "config.json").write_text('{"key": "value"}')
        
        print(f"临时项目：{temp_dir}")
        
        # 生成清单
        generator = ManifestGenerator(str(temp_dir))
        generator.scan(exclude_patterns=['*.json'])  # 排除 JSON 文件
        generator.save(str(temp_dir / 'manifest.json'))
        
        # 查看清单
        with open(temp_dir / 'manifest.json', 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        print(f"清单文件数：{manifest['total_files']}")
        print("文件列表：")
        for file_info in manifest['files']:
            print(f"  - {file_info['path']}")
        
        # 基于清单备份
        engine = BackupEngine()
        metadata = engine.backup_from_manifest(
            manifest_path=str(temp_dir / 'manifest.json'),
            name="selective-backup",
            compress=True
        )
        
        if metadata:
            print(f"\n[OK] 选择性备份成功！文件数：{metadata.files_count}")
            return True
        else:
            print("\n[FAIL] 选择性备份失败")
            return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    print("开始测试清单备份功能...\n")
    
    results = []
    
    # 测试完整流程
    results.append(("清单备份流程", test_manifest_backup()))
    
    # 测试选择性备份
    results.append(("选择性清单备份", test_selective_backup()))
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, s in results if s)
    print(f"\n总计：{passed}/{len(results)} 测试通过")
