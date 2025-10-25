import os
from pathlib import Path
from typing import Optional

# 存储用户自定义的路径
_USER_DATA_DIR_OVERRIDE: Optional[Path] = None

def get_builtin_data_dir() -> Path:
    """
    获取 chemetk 包内置的 'data' 目录路径 (只读)。

    Returns:
        Path: 指向 chemetk/data 目录的 Path 对象。
    """
    # __file__ 指向 chemetk/io/paths.py
    # .parent 是 chemetk/io
    # .parent.parent 是 chemetk
    builtin_dir = Path(__file__).parent.parent / 'data'
    return builtin_dir

def set_user_data_dir(path: str | Path):
    """
    允许用户在程序运行时手动指定一个可写的数据目录。
    一定要在导入其他模块之前指定！
    
    Args:
        path (str | Path): 用户指定的可写目录路径。
    """
    global _USER_DATA_DIR_OVERRIDE
    _USER_DATA_DIR_OVERRIDE = Path(path)
    # 确保目录存在
    _USER_DATA_DIR_OVERRIDE.mkdir(parents=True, exist_ok=True)
    print(f"用户数据目录已设置为: {_USER_DATA_DIR_OVERRIDE}")

def get_user_data_dir() -> Path:
    """
    获取用于存储缓存和下载数据的可写用户目录。

    优先级:
    1.  `set_user_data_dir()` 手动设置的路径。
    2.  `CHEMETK_USER_DATA` 环境变量。
    3.  操作系统的标准用户缓存/数据目录 (通过 platformdirs)。

    Returns:
        Path: 指向可写数据目录的 Path 对象。
    """
    global _USER_DATA_DIR_OVERRIDE
    
    # 1. 检查手动设置
    if _USER_DATA_DIR_OVERRIDE:
        return _USER_DATA_DIR_OVERRIDE

    # 2. 检查环境变量
    env_path = os.environ.get('CHEMETK_USER_DATA')
    if env_path:
        p = Path(env_path)
    else:
        # 3. 使用 platformdirs 确定平台特定的目录
        try:
            from platformdirs import user_cache_dir
            # user_cache_dir(appname, appauthor)
            p = Path(user_cache_dir('chemetk', 'ChemicalEngineeringToolkit'))
        except ImportError:
            print("警告: 'platformdirs' 未安装。将使用 .chemetk-cache 作为缓存目录。")
            print("请运行 'pip install platformdirs' 以获得更好的跨平台支持。")
            p = Path.home() / '.chemetk-cache'

    # 确保目录存在
    p.mkdir(parents=True, exist_ok=True)
    return p