# chemetk/data/__init__.py
"""
VLE数据管理模块

该模块提供对数据目录下所有VLE数据文件的自动发现和管理功能。
"""

from .vle_data_manager import VLEDataManager

# 使用单例模式，延迟初始化
_data_manager_instance = None

def _get_data_manager():
    """获取数据管理器实例（延迟初始化）"""
    global _data_manager_instance
    if _data_manager_instance is None:
        _data_manager_instance = VLEDataManager()
    return _data_manager_instance

# 导出便捷函数
def get_all_vle_files():
    """获取所有VLE数据文件信息"""
    return _get_data_manager().get_all_files()

def get_vle_file_path(system_name: str):
    """获取特定系统的VLE数据文件路径"""
    return _get_data_manager().get_file_path(system_name)

def list_vle_systems():
    """列出所有可用的VLE系统名称"""
    return _get_data_manager().list_available_systems()

def get_system_info(system_name: str):
    """获取特定系统的详细信息"""
    return _get_data_manager().get_system_info(system_name)

def print_vle_systems():
    """打印所有可用VLE系统的信息"""
    _get_data_manager().print_available_systems()

__all__ = [
    'VLEDataManager',
    'get_all_vle_files',
    'get_vle_file_path',
    'list_vle_systems', 
    'get_system_info',
    'print_vle_systems',
]

# 可选：在导入时自动扫描数据文件（取消注释如果需要）
# _data_manager_instance = VLEDataManager()


if __name__ == "__main__":
    # 测试代码
    print("VLE数据管理器测试")
    print("=" * 50)
    
    # 打印所有可用系统
    print_vle_systems()
    
    # 获取特定文件路径示例
    systems = list_vle_systems()
    if systems:
        first_system = systems[0]
        file_path = get_vle_file_path(first_system)
        print(f"系统 '{first_system}' 的文件路径: {file_path}")
        
        # 获取详细信息
        info = get_system_info(first_system)
        if info:
            print(f"详细信息: {info}")