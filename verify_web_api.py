#!/usr/bin/env python3
"""
OpenFinAgent Web UI 和 API 验证脚本

验证所有新创建的文件和依赖
"""

import sys
from pathlib import Path
from datetime import datetime

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    path = Path(filepath)
    if path.exists():
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} 不存在：{filepath}")
        return False

def check_import(module_name, description):
    """检查模块是否可以导入"""
    try:
        __import__(module_name)
        print_success(f"{description}: {module_name}")
        return True
    except ImportError as e:
        print_error(f"{description} 导入失败：{module_name} - {str(e)}")
        return False

def check_file_size(filepath, min_size=0):
    """检查文件大小"""
    path = Path(filepath)
    if not path.exists():
        return False
    
    size = path.stat().st_size
    if size >= min_size:
        print_success(f"{filepath} ({size/1024:.1f} KB)")
        return True
    else:
        print_error(f"{filepath} 文件太小 ({size} bytes)")
        return False

def main():
    print_header(f"OpenFinAgent Web UI 和 API 验证 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    project_root = Path(__file__).parent
    all_passed = True
    
    # 1. 检查 Web UI 文件
    print_header("1. 检查 Web UI 文件")
    
    web_pages = [
        (project_root / "web" / "pages" / "03_🤖_策略工厂.py", "策略工厂页面"),
        (project_root / "web" / "pages" / "04_📈_选股引擎.py", "选股引擎页面"),
        (project_root / "web" / "pages" / "05_🔔_监控中心.py", "监控中心页面"),
    ]
    
    for filepath, desc in web_pages:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 2. 检查 API 文件
    print_header("2. 检查 API 文件")
    
    api_files = [
        (project_root / "api" / "__init__.py", "API 主应用"),
        (project_root / "api" / "routes.py", "API 路由"),
        (project_root / "api" / "schemas.py", "API 数据结构"),
        (project_root / "api" / "run_api.py", "API 启动脚本"),
        (project_root / "api" / "README.md", "API 文档"),
    ]
    
    for filepath, desc in api_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 3. 检查测试文件
    print_header("3. 检查测试文件")
    
    test_files = [
        (project_root / "tests" / "api" / "test_api.py", "API 集成测试"),
    ]
    
    for filepath, desc in test_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 4. 检查文档
    print_header("4. 检查文档")
    
    docs = [
        (project_root / "docs" / "WEB_UI_API_DEVELOPMENT.md", "开发报告"),
        (project_root / "QUICKSTART_WEB_API.md", "快速启动指南"),
    ]
    
    for filepath, desc in docs:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 5. 检查文件大小
    print_header("5. 检查文件大小")
    
    files_to_check = [
        (project_root / "web" / "pages" / "03_🤖_策略工厂.py", 5000),
        (project_root / "web" / "pages" / "04_📈_选股引擎.py", 5000),
        (project_root / "web" / "pages" / "05_🔔_监控中心.py", 5000),
        (project_root / "api" / "__init__.py", 5000),
        (project_root / "api" / "routes.py", 5000),
        (project_root / "api" / "schemas.py", 5000),
    ]
    
    for filepath, min_size in files_to_check:
        if not check_file_size(filepath, min_size):
            all_passed = False
    
    # 6. 检查 Python 语法
    print_header("6. 检查 Python 语法")
    
    python_files = [
        project_root / "api" / "__init__.py",
        project_root / "api" / "routes.py",
        project_root / "api" / "schemas.py",
        project_root / "web" / "pages" / "03_🤖_策略工厂.py",
        project_root / "web" / "pages" / "04_📈_选股引擎.py",
        project_root / "web" / "pages" / "05_🔔_监控中心.py",
    ]
    
    for filepath in python_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                compile(f.read(), filepath, 'exec')
            print_success(f"语法正确：{filepath.name}")
        except SyntaxError as e:
            print_error(f"语法错误：{filepath.name} - {str(e)}")
            all_passed = False
    
    # 7. 检查依赖
    print_header("7. 检查关键依赖")
    
    dependencies = [
        ("streamlit", "Streamlit Web 框架"),
        ("fastapi", "FastAPI Web 框架"),
        ("uvicorn", "Uvicorn ASGI 服务器"),
        ("pydantic", "数据验证"),
        ("pandas", "数据处理"),
    ]
    
    for module, desc in dependencies:
        try:
            __import__(module)
            print_success(f"{desc}: {module}")
        except ImportError:
            print_warning(f"{desc} 未安装：{module}")
    
    # 8. 统计信息
    print_header("8. 统计信息")
    
    total_files = 0
    total_size = 0
    
    for filepath in python_files + [f[0] for f in api_files] + [f[0] for f in test_files] + [f[0] for f in docs]:
        if filepath.exists():
            total_files += 1
            total_size += filepath.stat().st_size
    
    print_info(f"总文件数：{total_files}")
    print_info(f"总代码量：{total_size/1024:.1f} KB")
    
    # 总结
    print_header("验证总结")
    
    if all_passed:
        print_success("✅ 所有检查通过！Web UI 和 API 开发完成！")
        print_info("\n下一步:")
        print_info("1. 启动 Web UI: cd web && streamlit run app.py")
        print_info("2. 启动 API: python api/run_api.py")
        print_info("3. 查看文档：api/README.md")
    else:
        print_error("❌ 部分检查未通过，请检查上述错误")
        sys.exit(1)
    
    print()

if __name__ == "__main__":
    main()
