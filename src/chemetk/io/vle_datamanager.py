import os
import json
import glob
from typing import Dict, List, Optional
from pathlib import Path
from . import paths  # 导入统一的路径管理器

class VLEManager:
    """
    VLE数据管理器，用于自动发现和管理 VLE 数据文件。

    它会从两个位置加载数据：
    1.  包内置的 'data' 目录 (只读)。
    2.  用户可写的 'vle' 数据目录 (位于 `paths.get_user_data_dir() / 'vle'`)。

    如果两个位置存在同名文件 (例如 'system1.json')，
    用户目录中的文件将优先被加载。
    """
    
    def __init__(self):
        """
        初始化数据管理器。
        """
        # 1. 定义包内只读数据目录
        self.builtin_data_dir = paths.get_builtin_data_dir()
        
        # 2. 定义用户可写VLE数据目录 (在nist缓存旁边)
        self.user_vle_dir = paths.get_user_data_dir() / 'vle'
        
        # 确保用户VLE目录存在，以便用户可以向其中添加文件
        if not self.user_vle_dir.exists():
            self.user_vle_dir.mkdir(parents=True, exist_ok=True)
            print(f"用户VLE数据目录不存在，已自动创建：{self.user_vle_dir}")
            
        self._data_files = {}
        self._load_data_files()
    
    def _load_files_from_path(self, data_path: Path):
        """
        辅助函数：从指定路径加载所有 .json 文件到 self._data_files
        """
        json_pattern = str(data_path / "*.json")
        json_files = glob.glob(json_pattern)
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                name = data.get("name", os.path.splitext(os.path.basename(json_file))[0])
                
                file_info = {
                    "name": name,
                    "path": os.path.abspath(json_file),
                    "filename": os.path.basename(json_file),
                    "components": data.get("components", ["Component_A", "Component_B"])
                }
                
                # 使用文件名（不含扩展名）作为键
                key = os.path.splitext(os.path.basename(json_file))[0]
                
                # 如果键已存在，此操作会覆盖它（实现用户文件优先）
                self._data_files[key] = file_info
                
            except (json.JSONDecodeError, KeyError, IOError) as e:
                print(f"警告: 无法加载文件 {json_file}: {e}")
                continue

    def _load_data_files(self):
        """
        加载所有 VLE 数据文件。
        
        顺序:
        1.  先加载包内数据。
        2.  再加载用户数据 (同名文件将覆盖包内数据)。
        """
        print(f"正在从包内目录加载VLE数据: {self.builtin_data_dir}")
        self._load_files_from_path(self.builtin_data_dir)
        
        print(f"正在从用户目录加载VLE数据: {self.user_vle_dir}")
        self._load_files_from_path(self.user_vle_dir)
        
        if not self._data_files:
            print(f"警告: 在 {self.builtin_data_dir} 和 {self.user_vle_dir} 中均未找到 VLE .json 文件。")

    # ... (get_all_files, get_file_by_name, get_file_path, ... )
    # ... (list_available_systems, get_system_info, print_available_systems)
    # 【注意】所有其他方法 (get_all_files, get_system_info 等) 保持不变。
    # 我在这里再次复制它们以保证完整性。

    def get_all_files(self) -> Dict[str, Dict]:
        return self._data_files.copy()

    def get_file_by_filename(self, filename: str) -> Optional[Dict]:
        return self._data_files.get(filename)

    def get_file_path_by_filename(self, filename: str) -> Optional[str]:
        file_info = self._data_files.get(filename)
        return file_info["path"] if file_info else None

    def list_available_systems(self) -> List[str]:
        return list(self._data_files.keys())

    def get_system_info_by_filename(self, filename: str) -> Optional[Dict]:
        file_info = self._data_files.get(filename)
        if not file_info:
            return None
        
        try:
            with open(file_info["path"], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data_points = data.get("data", [])
            total_points = len(data_points)
            
            alpha_points = len([p for p in data_points if p.get("alpha") is not None])
            has_alpha = alpha_points >= 2
            
            temps = [p["temp"] for p in data_points if "temp" in p]
            temp_range = (min(temps), max(temps)) if temps else (None, None)
            
            x_values = [p["x"] for p in data_points if "x" in p]
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
        except (json.JSONDecodeError, IOError, KeyError, TypeError) as e:
            print(f"警告: 无法读取系统 {name} 的详细信息: {e}")
            return None

    def print_available_systems(self):
        print("可用的VLE系统:")
        print(f"(从 {self.builtin_data_dir} 和 {self.user_vle_dir} 加载)")
        print("-" * 80)
        
        if not self._data_files:
            print("未找到任何系统。")
            return
            
        for key in self.list_available_systems():
            info = self.get_system_info(key)
            if info:
                # 检查文件路径以判断来源
                is_user_file = Path(info['file_path']).parent == self.user_vle_dir
                source_tag = "[用户]" if is_user_file else "[内置]"
                
                alpha_status = "有" if info["has_alpha_data"] else "无"
                temp_range_str = f"{info['temperature_range'][0]:.1f} - {info['temperature_range'][1]:.1f} °C" if all(info['temperature_range']) else "N/A"
                comp_range_str = f"x = {info['composition_range'][0]:.3f} - {info['composition_range'][1]:.3f}" if all(info['composition_range']) else "N/A"

                print(f"系统: {info['name']} {source_tag}")
                print(f"  键名: {key}")
                print(f"  组分: {' - '.join(info['components'])}")
                print(f"  数据点: {info['data_points']} 个")
                print(f"  相对挥发度数据: {alpha_status} ({info['alpha_data_points']} 个点)")
                print(f"  温度范围: {temp_range_str}")
                print(f"  组成范围: {comp_range_str}")
                print(f"  文件: {os.path.basename(info['file_path'])}")
                print()