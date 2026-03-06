#!/usr/bin/env python3
"""
组件测试脚本 - 验证文件结构和导入
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_file_structure():
    """测试文件结构"""
    print("📁 测试文件结构...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "components/__init__.py",
        "components/loading.py",
        "components/navigation.py",
        "components/charts.py",
        "components/cards.py",
        "pages/home.py",
        "pages/create.py",
        "pages/backtest.py",
        "pages/compare.py",
        "pages/templates.py",
        "pages/monitor.py",
        "utils/__init__.py",
        "utils/cache.py",
        "utils/theme.py",
        "utils/export.py",
        "styles/main.css",
        "ENHANCEMENTS.md"
    ]
    
    missing = []
    for file in required_files:
        if not (project_root / file).exists():
            missing.append(file)
            print(f"  ❌ 缺失：{file}")
        else:
            print(f"  ✅ 存在：{file}")
    
    if missing:
        print(f"\n❌ 缺失 {len(missing)} 个文件")
        return False
    else:
        print(f"\n✅ 所有 {len(required_files)} 个文件都存在")
        return True


def test_syntax():
    """测试 Python 语法"""
    print("\n🔍 测试 Python 语法...")
    
    import py_compile
    import tempfile
    
    python_files = [
        "app.py",
        "components/loading.py",
        "components/navigation.py",
        "components/charts.py",
        "components/cards.py",
        "pages/home.py",
        "pages/templates.py",
        "pages/monitor.py",
        "utils/cache.py",
        "utils/theme.py",
        "utils/export.py"
    ]
    
    errors = []
    for file in python_files:
        try:
            py_compile.compile(project_root / file, doraise=True)
            print(f"  ✅ 语法正确：{file}")
        except py_compile.PyCompileError as e:
            errors.append((file, str(e)))
            print(f"  ❌ 语法错误：{file} - {e}")
    
    if errors:
        print(f"\n❌ {len(errors)} 个文件有语法错误")
        return False
    else:
        print(f"\n✅ 所有 Python 文件语法正确")
        return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("OpenFinAgent Web UI 增强版 - 组件测试")
    print("=" * 60)
    
    test1 = test_file_structure()
    test2 = test_syntax()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("✅ 所有测试通过！")
        print("\n🚀 下一步:")
        print("1. 安装依赖：pip install -r requirements.txt")
        print("2. 运行应用：streamlit run app.py")
        print("3. 访问：http://localhost:8501")
    else:
        print("❌ 部分测试失败，请检查上方错误信息")
    print("=" * 60)


if __name__ == "__main__":
    main()
