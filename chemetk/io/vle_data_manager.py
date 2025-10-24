import os
import json
import glob
from typing import Dict, List, Optional

class VLEDataManager:
    """
    VLE数据管理器，用于自动发现和管理数据目录下的所有VLE数据文件
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化数据管理器
        
        参数:
        data_dir : str, optional - 数据目录路径，如果为None则使用当前文件所在目录
        """
        if data_dir is None:
            # 获取当前文件所在目录的上级目录，再拼接data文件夹
            current_file_dir = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在目录
            parent_dir = os.path.dirname(current_file_dir)  # 上级目录
            data_dir = os.path.join(parent_dir, "data")  # 上级目录下的data文件夹
        
        self.data_dir = data_dir
        self._data_files = {}
        self._load_data_files()
    
    def _load_data_files(self):
        """加载数据目录下的所有JSON文件"""
        # 查找所有JSON文件
        json_pattern = os.path.join(self.data_dir, "*.json")
        json_files = glob.glob(json_pattern)
        
        for json_file in json_files:
            try:
                # 读取JSON文件获取名称
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取name字段，如果不存在则使用文件名
                name = data.get("name", os.path.splitext(os.path.basename(json_file))[0])
                
                # 存储文件信息
                file_info = {
                    "name": name,
                    "path": os.path.abspath(json_file),
                    "filename": os.path.basename(json_file),
                    "components": data.get("components", ["Component_A", "Component_B"])
                }
                
                # 使用文件名（不含扩展名）作为键
                key = os.path.splitext(os.path.basename(json_file))[0]
                self._data_files[key] = file_info
                
            except (json.JSONDecodeError, KeyError, IOError) as e:
                print(f"警告: 无法加载文件 {json_file}: {e}")
                continue
    
    def get_all_files(self) -> Dict[str, Dict]:
        """
        获取所有数据文件的信息
        
        返回:
        Dict[str, Dict] - 文件名到文件信息的映射
        """
        return self._data_files.copy()
    
    def get_file_by_name(self, name: str) -> Optional[Dict]:
        """
        根据名称获取数据文件信息
        
        参数:
        name : str - 数据文件名（不含扩展名）
        
        返回:
        Optional[Dict] - 文件信息字典，如果不存在则返回None
        """
        return self._data_files.get(name)
    
    def get_file_path(self, name: str) -> Optional[str]:
        """
        根据名称获取数据文件的绝对路径
        
        参数:
        name : str - 数据文件名（不含扩展名）
        
        返回:
        Optional[str] - 文件绝对路径，如果不存在则返回None
        """
        file_info = self._data_files.get(name)
        return file_info["path"] if file_info else None
    
    def list_available_systems(self) -> List[str]:
        """
        获取所有可用的系统名称列表
        
        返回:
        List[str] - 系统名称列表
        """
        return list(self._data_files.keys())
    
    def get_system_info(self, name: str) -> Optional[Dict]:
        """
        获取特定系统的详细信息
        
        参数:
        name : str - 系统名称
        
        返回:
        Optional[Dict] - 系统信息字典
        """
        file_info = self._data_files.get(name)
        if not file_info:
            return None
        
        try:
            with open(file_info["path"], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 计算数据点统计信息
            data_points = data.get("data", [])
            total_points = len(data_points)
            
            # 检查是否有alpha数据
            alpha_points = len([p for p in data_points if p.get("alpha") is not None])
            has_alpha = alpha_points >= 2
            
            # 温度范围
            temps = [p["temp"] for p in data_points]
            temp_range = (min(temps), max(temps)) if temps else (None, None)
            
            # 组成范围
            x_values = [p["x"] for p in data_points]
            x_range = (min(x_values), max(x_values)) if x_values else (None, None)
            
            return {
                "name": data.get("name", name),
                "components": data.get("components", ["Component_A", "Component_B"]),
                "file_path": file_info["path"],
                "data_points": total_points,
                "has_alpha_data": has_alpha,
                "alpha_data_points": alpha_points,
                "temperature_range": temp_range,
                "composition_range": x_range
            }
            
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"警告: 无法读取系统 {name} 的详细信息: {e}")
            return None
    
    def print_available_systems(self):
        """打印所有可用系统的信息"""
        print("可用的VLE系统:")
        print("-" * 80)
        for key, info in self._data_files.items():
            system_info = self.get_system_info(key)
            if system_info:
                alpha_status = "有" if system_info["has_alpha_data"] else "无"
                print(f"系统: {system_info['name']}")
                print(f"  键名: {key}")
                print(f"  组分: {system_info['components'][0]} - {system_info['components'][1]}")
                print(f"  数据点: {system_info['data_points']} 个")
                print(f"  相对挥发度数据: {alpha_status} ({system_info['alpha_data_points']} 个点)")
                print(f"  温度范围: {system_info['temperature_range'][0]:.1f} - {system_info['temperature_range'][1]:.1f} °C")
                print(f"  组成范围: x = {system_info['composition_range'][0]:.3f} - {system_info['composition_range'][1]:.3f}")
                print(f"  文件: {info['filename']}")
                print()
