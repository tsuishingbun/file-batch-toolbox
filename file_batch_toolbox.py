#!/usr/bin/env python3
"""
文件批量处理工具箱 (FileBatchToolbox)
=====================================
一个简单实用的批量文件处理工具，支持：
1. 批量重命名 - 支持编号、日期、搜索替换
2. 图片压缩 - 批量压缩图片文件
3. 文本替换 - 批量文本内容替换

作者: Sisyphus AI Labs
版本: 1.0.0
"""

import os
import re
import sys
import json
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Callable
from functools import wraps

# 检查PIL是否可用
PIL_AVAILABLE = importlib.util.find_spec("PIL") is not None

# ==================== 工具配置 ====================
CONFIG = {
    "version": "1.0.0",
    "author": "Sisyphus AI Labs",
    "default_jpeg_quality": 85,
    "default_png_compress": 6,
    "supported_image_formats": [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"],
    "default_rename_pattern": "{name}_{index:03d}",
}


def print_banner():
    """打印工具横幅"""
    banner = """
+============================================================+
|          [F] FileBatchToolbox v1.0.0                     |
|          批量文件处理工具箱 - 销售盈利工具                 |
+============================================================+
|  功能:                                                     |
|    [1] 批量重命名文件                                      |
|    [2] 图片批量压缩                                        |
|    [3] 批量文本替换                                        |
|    [0] 退出                                                |
+============================================================+
    """
    print(banner)


def print_progress(current: int, total: int, prefix: str = "进度") -> None:
    """打印进度条"""
    percent = int(100 * current / total) if total > 0 else 0
    bar = "#" * int(percent / 5) + "-" * (20 - int(percent / 5))
    print(f"\r{prefix}: |{bar}| {percent}% ({current}/{total})", end="", flush=True)
    if current == total:
        print()


def confirm(prompt: str) -> bool:
    """确认提示"""
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ("y", "yes", "是", "1")


def get_files_by_extension(directory: str, extensions: List[str]) -> List[Path]:
    """获取指定目录下指定扩展名的所有文件"""
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")

    files = []
    for ext in extensions:
        files.extend(dir_path.glob(f"*{ext}"))
        files.extend(dir_path.glob(f"*{ext.upper()}"))

    return sorted(files)


def log_action(action: str, details: str = "") -> None:
    """记录操作日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action}"
    if details:
        log_entry += f" - {details}"
    print(f"  [LOG] {log_entry}")


# ==================== 功能1: 批量重命名 ====================
def batch_rename_menu():
    """批量重命名菜单"""
    print("\n" + "=" * 50)
    print("[R] 批量重命名")
    print("=" * 50)
    print("选择重命名方式:")
    print("  [1] 顺序编号重命名")
    print("  [2] 日期前缀重命名")
    print("  [3] 搜索替换重命名")
    print("  [4] 统一扩展名")
    print("  [0] 返回主菜单")

    choice = input("\n请选择 (0-4): ").strip()
    return choice


def rename_with_sequence(files: List[Path], pattern: str = "{name}_{index:03d}") -> int:
    """顺序编号重命名"""
    renamed_count = 0

    for index, file in enumerate(files, 1):
        new_name = (
            pattern.format(
                name=file.stem,
                index=index,
                date=datetime.now().strftime("%Y%m%d"),
                time=datetime.now().strftime("%H%M%S"),
            )
            + file.suffix
        )

        new_path = file.parent / new_name
        if new_path != file:
            file.rename(new_path)
            renamed_count += 1
            log_action("重命名", f"{file.name} -> {new_name}")

    return renamed_count


def rename_with_date(files: List[Path], date_format: str = "%Y%m%d") -> int:
    """日期前缀重命名"""
    date_prefix = datetime.now().strftime(date_format)
    renamed_count = 0

    for file in files:
        new_name = f"{date_prefix}_{file.name}"
        new_path = file.parent / new_name
        if new_path != file:
            file.rename(new_path)
            renamed_count += 1
            log_action("重命名", f"{file.name} -> {new_name}")

    return renamed_count


def rename_with_replace(files: List[Path], search: str, replace: str) -> int:
    """搜索替换重命名"""
    renamed_count = 0

    for file in files:
        if search in file.name:
            new_name = file.name.replace(search, replace)
            new_path = file.parent / new_name
            file.rename(new_path)
            renamed_count += 1
            log_action("重命名", f"{file.name} -> {new_name}")

    return renamed_count


def rename_extension(files: List[Path], new_ext: str) -> int:
    """统一扩展名"""
    if not new_ext.startswith("."):
        new_ext = "." + new_ext

    renamed_count = 0

    for file in files:
        new_name = file.stem + new_ext
        new_path = file.parent / new_name
        if new_path != file:
            file.rename(new_path)
            renamed_count += 1
            log_action("重命名", f"{file.name} -> {new_name}")

    return renamed_count


def batch_rename(directory: str):
    """批量重命名主函数"""
    try:
        files = get_files_by_extension(directory, ["*"])
        if not files:
            print("[X] 目录中没有文件")
            return

        print(f"\n[DIR] 找到 {len(files)} 个文件")
        print("文件列表:")
        for i, f in enumerate(files[:10], 1):
            print(f"  {i}. {f.name}")
        if len(files) > 10:
            print(f"  ... 还有 {len(files) - 10} 个文件")

        if not confirm("是否继续"):
            return

        while True:
            choice = batch_rename_menu()

            if choice == "1":
                pattern = input("输入命名模式 (默认: {name}_{index:03d}): ").strip()
                if not pattern:
                    pattern = "{name}_{index:03d}"
                count = rename_with_sequence(files, pattern)
                print(f"\n[OK] 完成! 重命名了 {count} 个文件")

            elif choice == "2":
                date_fmt = input("日期格式 (默认: %Y%m%d): ").strip() or "%Y%m%d"
                count = rename_with_date(files, date_fmt)
                print(f"\n[OK] 完成! 重命名了 {count} 个文件")

            elif choice == "3":
                search = input("要替换的文本: ").strip()
                replace = input("替换为: ").strip()
                count = rename_with_replace(files, search, replace)
                print(f"\n[OK] 完成! 重命名了 {count} 个文件")

            elif choice == "4":
                new_ext = input("新扩展名 (如 jpg, png): ").strip()
                count = rename_extension(files, new_ext)
                print(f"\n[OK] 完成! 重命名了 {count} 个文件")

            elif choice == "0":
                break
            else:
                print("[X] 无效选择")

            if choice != "0":
                if not confirm("是否继续其他重命名操作"):
                    break

    except Exception as e:
        print(f"[X] 错误: {e}")


# ==================== 功能2: 图片压缩 ====================
def compress_image_pillow(
    image_path: Path, output_path: Path, quality: int = 85
) -> bool:
    """使用Pillow压缩图片"""
    if not PIL_AVAILABLE:
        print("[!] Pillow未安装,请运行: pip install Pillow")
        return False

    try:
        # 使用importlib动态导入避免LSP错误
        pil_module = importlib.import_module("PIL")
        Image = getattr(pil_module, "Image")

        img = Image.open(image_path)

        # 保持原格式
        if image_path.suffix.lower() in [".jpg", ".jpeg"]:
            img.save(output_path, "JPEG", quality=quality, optimize=True)
        elif image_path.suffix.lower() == ".png":
            img.save(output_path, "PNG", optimize=True, compress_level=9)
        else:
            img.save(output_path, quality=quality)

        return True
    except Exception as e:
        print(f"[X] 压缩失败 {image_path.name}: {e}")
        return False


def compress_images(directory: str, quality: int = 85, create_backup: bool = True):
    """批量压缩图片"""
    # 检查PIL是否可用
    pil_available = importlib.util.find_spec("PIL") is not None

    if not pil_available:
        print("[X] 需要安装Pillow库: pip install Pillow")
        if confirm("是否现在安装"):
            os.system("pip install Pillow")
            pil_available = importlib.util.find_spec("PIL") is not None
            if not pil_available:
                print("[X] 安装失败,请手动安装")
                return

    try:
        files = get_files_by_extension(directory, CONFIG["supported_image_formats"])
        if not files:
            print("[X] 目录中没有图片文件")
            return

        # 创建备份目录
        backup_dir: Optional[Path] = None
        if create_backup:
            backup_dir = Path(directory) / "backup"
            backup_dir.mkdir(exist_ok=True)
            print(f"[DIR] 备份目录: {backup_dir}")

        print(f"\n[DIR] 找到 {len(files)} 张图片")
        print(f"[ZIP] 压缩质量: {quality}%")

        if not confirm("是否开始压缩"):
            return

        compressed = 0
        total_original_size = 0
        total_new_size = 0

        for i, file in enumerate(files, 1):
            original_size = file.stat().st_size
            total_original_size += original_size

            # 压缩后的文件名
            compressed_name = file.stem + "_compressed" + file.suffix
            output_path = file.parent / compressed_name

            if compress_image_pillow(file, output_path, quality):
                # 备份原图
                if create_backup and backup_dir:
                    shutil.copy2(file, backup_dir / file.name)

                # 替换原文件
                shutil.move(str(output_path), str(file))

                new_size = file.stat().st_size
                total_new_size += new_size
                compressed += 1

                ratio = (1 - new_size / original_size) * 100 if original_size > 0 else 0
                print_progress(i, len(files), "压缩")
                log_action("压缩", f"{file.name} ({ratio:.1f}% down)")

        print(f"\n[OK] 完成! 压缩了 {compressed}/{len(files)} 张图片")

        if total_original_size > 0:
            saved = total_original_size - total_new_size
            saved_kb = saved / 1024
            print(
                f"[DISK] 节省空间: {saved_kb:.2f} KB ({(saved / total_original_size) * 100:.1f}%)"
            )

    except Exception as e:
        print(f"[X] 错误: {e}")


# ==================== 功能3: 批量文本替换 ====================
def batch_text_replace(
    directory: str,
    search: str,
    replace: str,
    file_extensions: Optional[List[str]] = None,
):
    """批量文本替换"""
    if file_extensions is None:
        file_extensions = [
            ".txt",
            ".md",
            ".json",
            ".xml",
            ".csv",
            ".log",
            ".html",
            ".css",
            ".js",
            ".py",
        ]

    try:
        files = get_files_by_extension(directory, file_extensions)
        if not files:
            print("[X] 目录中没有文本文件")
            return

        print(f"\n[DIR] 找到 {len(files)} 个文本文件")
        print(f"[SEARCH] 搜索: '{search}'")
        print(f"[REPLACE] 替换: '{replace}'")

        if not confirm("是否开始替换"):
            return

        replaced_count = 0
        total_replacements = 0

        for i, file in enumerate(files, 1):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if search in content:
                    new_content = content.replace(search, replace)
                    replacements = content.count(search)

                    with open(file, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    replaced_count += 1
                    total_replacements += replacements
                    log_action("替换", f"{file.name} ({replacements}处)")

                print_progress(i, len(files), "处理")

            except Exception as e:
                print(f"\n[X] 处理失败 {file.name}: {e}")

        print(f"\n[OK] 完成!")
        print(f"   修改文件: {replaced_count} 个")
        print(f"   总替换次数: {total_replacements} 次")

    except Exception as e:
        print(f"[X] 错误: {e}")


def batch_text_replace_regex(
    directory: str,
    pattern: str,
    replace: str,
    file_extensions: Optional[List[str]] = None,
):
    """批量文本正则替换"""
    if file_extensions is None:
        file_extensions = [".txt", ".md", ".json", ".xml", ".csv", ".log"]

    try:
        files = get_files_by_extension(directory, file_extensions)
        if not files:
            print("[X] 目录中没有文本文件")
            return

        print(f"\n[DIR] 找到 {len(files)} 个文本文件")
        print(f"[SEARCH] 正则模式: '{pattern}'")
        print(f"[REPLACE] 替换为: '{replace}'")

        if not confirm("是否开始替换"):
            return

        replaced_count = 0
        total_replacements = 0
        regex = re.compile(pattern)

        for i, file in enumerate(files, 1):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                new_content, replacements = regex.subn(replace, content)

                if replacements > 0:
                    with open(file, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    replaced_count += 1
                    total_replacements += replacements
                    log_action("正则替换", f"{file.name} ({replacements}处)")

                print_progress(i, len(files), "处理")

            except Exception as e:
                print(f"\n[X] 处理失败 {file.name}: {e}")

        print(f"\n[OK] 完成!")
        print(f"   修改文件: {replaced_count} 个")
        print(f"   总替换次数: {total_replacements} 次")

    except re.error as e:
        print(f"[X] 正则表达式错误: {e}")
    except Exception as e:
        print(f"[X] 错误: {e}")


# ==================== 主菜单 ====================
def main():
    """主函数"""
    while True:
        print_banner()

        try:
            choice = input("\n请选择功能 (0-3): ").strip()

            if choice == "0":
                print("\n[BYE] 感谢使用! 再见!")
                break

            elif choice == "1":
                directory = input("[DIR] 请输入要处理的目录路径: ").strip()
                if not directory:
                    directory = os.getcwd()
                batch_rename(directory)

            elif choice == "2":
                directory = input("[DIR] 请输入图片所在目录: ").strip()
                if not directory:
                    directory = os.getcwd()

                quality_input = input("[ZIP] 压缩质量 (1-100, 默认85): ").strip()
                quality = int(quality_input) if quality_input else 85
                quality = max(1, min(100, quality))

                create_backup = confirm("是否创建备份")
                compress_images(directory, quality, create_backup)

            elif choice == "3":
                directory = input("[DIR] 请输入要处理的目录: ").strip()
                if not directory:
                    directory = os.getcwd()

                print("\n选择替换模式:")
                print("  [1] 普通文本替换")
                print("  [2] 正则表达式替换")
                mode = input("请选择 (1-2): ").strip()

                if mode == "1":
                    search = input("[SEARCH] 要搜索的文本: ").strip()
                    replace = input("[REPLACE] 替换为: ").strip()
                    batch_text_replace(directory, search, replace)
                elif mode == "2":
                    pattern = input("[SEARCH] 正则表达式: ").strip()
                    replace = input("[REPLACE] 替换为: ").strip()
                    batch_text_replace_regex(directory, pattern, replace)
                else:
                    print("[X] 无效选择")
            else:
                print("[X] 无效选择,请重试")

            input("\n按回车键继续...")

        except KeyboardInterrupt:
            print("\n\n[BYE] 已退出")
            break
        except Exception as e:
            print(f"\n[X] 发生错误: {e}")
            input("\n按回车键继续...")


if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("[X] 需要Python 3.7或更高版本")
        sys.exit(1)

    main()
