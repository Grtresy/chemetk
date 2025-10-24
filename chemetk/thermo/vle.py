# chemetk/thermo/vle.py
import json
import numpy as np
from scipy.interpolate import interp1d

class VLE:
    """
    处理二元体系汽液平衡(VLE)数据。
    通过加载数据文件并使用插值，提供不同组分下的热力学性质。
    """
    def __init__(self, data_path: str):
        """
        从JSON文件加载VLE数据并初始化插值函数。
        
        :param data_path: VLE数据文件的路径 (JSON格式)。
        """
        with open(data_path, 'r') as f:
            raw_data = json.load(f)

        self.name = raw_data.get("name", "Unnamed VLE Data")
        self.components = raw_data.get("components", ["A", "B"])
        self.data_points = raw_data["data"]
        
        # 提取数据用于插值
        self.temps = np.array([point["temp"] for point in self.data_points])
        self.y_values = np.array([point["y"] for point in self.data_points])
        self.x_values = np.array([point["x"] for point in self.data_points])
        
        # 处理相对挥发度数据（可能不存在）
        alpha_data_points = [point for point in self.data_points if point.get("alpha") is not None]
        self.has_alpha = len(alpha_data_points) > 0

        if self.has_alpha:
            # 只有有相对挥发度的数据点
            alpha_data_points = [point for point in self.data_points if point.get("alpha") is not None]
            self.alpha_temps = np.array([point["temp"] for point in alpha_data_points])
            self.alpha_values = np.array([point["alpha"] for point in alpha_data_points])
            self.alpha_x_values = np.array([point["x"] for point in alpha_data_points])
        
        # 创建插值函数
        # 从液相组成(x)插值温度
        self.temp_from_x = interp1d(self.x_values, self.temps, kind='cubic', bounds_error=False, fill_value=np.nan)
        
        # 从气相组成(y)插值温度
        self.temp_from_y = interp1d(self.y_values, self.temps, kind='cubic', bounds_error=False, fill_value=np.nan)
        
        # 从液相组成(x)插值气相组成(y)
        self.y_from_x = interp1d(self.x_values, self.y_values, kind='cubic', bounds_error=False, fill_value=np.nan)
        
        # 从气相组成(y)插值液相组成(x)
        self.x_from_y = interp1d(self.y_values, self.x_values, kind='cubic', bounds_error=False, fill_value=np.nan)
        
        # 从温度插值液相组成(x)
        self.x_from_temp = interp1d(self.temps, self.x_values, kind='cubic', bounds_error=False, fill_value=np.nan)
        
        # 从温度插值气相组成(y)
        self.y_from_temp = interp1d(self.temps, self.y_values, kind='cubic', bounds_error=False, fill_value=np.nan)
        
        # 相对挥发度插值函数（如果数据存在）
        if self.has_alpha:
            if len(self.alpha_x_values) > 1:
                self.alpha_from_x = interp1d(self.alpha_x_values, self.alpha_values, kind='cubic', bounds_error=False, fill_value=np.nan)
                self.alpha_from_temp = interp1d(self.alpha_temps, self.alpha_values, kind='cubic', bounds_error=False, fill_value=np.nan)
            else:
                self.alpha_from_x = lambda x: np.full_like(x, np.nan) if hasattr(x, '__len__') else np.nan
                self.alpha_from_temp = lambda t: np.full_like(t, np.nan) if hasattr(t, '__len__') else np.nan
        else:
            self.alpha_from_x = lambda x: np.full_like(x, np.nan) if hasattr(x, '__len__') else np.nan
            self.alpha_from_temp = lambda t: np.full_like(t, np.nan) if hasattr(t, '__len__') else np.nan
    
    def get_temperature_by_x(self, x):
        """
        根据液相组分1摩尔分数获取温度
        
        参数:
        x : float or array-like - 液相组分1摩尔分数 (0.0 - 1.0)
        
        返回:
        float or array - 温度 (°C)
        """
        return self.temp_from_x(x)
    
    def get_temperature_by_y(self, y):
        """
        根据气相组分1摩尔分数获取温度
        
        参数:
        y : float or array-like - 气相组分1摩尔分数 (0.0 - 1.0)
        
        返回:
        float or array - 温度 (°C)
        """
        return self.temp_from_y(y)
    
    def get_y_by_x(self, x):
        """
        根据液相组分1摩尔分数获取气相组分1摩尔分数
        
        参数:
        x : float or array-like - 液相组分1摩尔分数 (0.0 - 1.0)
        
        返回:
        float or array - 气相组分1摩尔分数 (0.0 - 1.0)
        """
        return self.y_from_x(x)
    
    def get_x_by_y(self, y):
        """
        根据气相组分1摩尔分数获取液相组分1摩尔分数
        
        参数:
        y : float or array-like - 气相组分1摩尔分数 (0.0 - 1.0)
        
        返回:
        float or array - 液相组分1摩尔分数 (0.0 - 1.0)
        """
        return self.x_from_y(y)
    
    def get_alpha_by_x(self, x):
        """
        根据液相组分1摩尔分数获取相对挥发度
        
        参数:
        x : float or array-like - 液相组分1摩尔分数 (0.0 - 1.0)
        
        返回:
        float or array - 相对挥发度
        """
        return self.alpha_from_x(x)
    
    def get_alpha_by_temp(self, temp):
        """
        根据温度获取相对挥发度
        
        参数:
        temp : float or array-like - 温度 (°C)
        
        返回:
        float or array - 相对挥发度
        """
        return self.alpha_from_temp(temp)
    
    def get_x_by_temp(self, temp):
        """
        根据温度获取液相组分1摩尔分数
        
        参数:
        temp : float or array-like - 温度 (°C)
        
        返回:
        float or array - 液相组分1摩尔分数 (0.0 - 1.0)
        """
        return self.x_from_temp(temp)
    
    def get_y_by_temp(self, temp):
        """
        根据温度获取气相组分1摩尔分数
        
        参数:
        temp : float or array-like - 温度 (°C)
        
        返回:
        float or array - 气相组分1摩尔分数 (0.0 - 1.0)
        """
        return self.y_from_temp(temp)
    
    def get_all_properties_by_x(self, x):
        """
        根据液相组分1摩尔分数获取所有相关性质
        
        参数:
        x : float - 液相组分1摩尔分数 (0.0 - 1.0)
        
        返回:
        dict - 包含温度、气相组成、相对挥发度的字典
        """
        temp = self.get_temperature_by_x(x)
        y = self.get_y_by_x(x)
        alpha = self.get_alpha_by_x(x)
        return {
            "temperature": temp,
            "vapor_composition": y,
            "liquid_composition": x,
            "relative_volatility": alpha
        }
    
    def get_all_properties_by_temp(self, temp):
        """
        根据温度获取所有相关性质
        
        参数:
        temp : float - 温度 (°C)
        
        返回:
        dict - 包含液相组成、气相组成、相对挥发度的字典
        """
        x = self.get_x_by_temp(temp)
        y = self.get_y_by_temp(temp)
        alpha = self.get_alpha_by_temp(temp)
        return {
            "temperature": temp,
            "vapor_composition": y,
            "liquid_composition": x,
            "relative_volatility": alpha
        }
    
    def get_boiling_point_component_a(self):
        """
        获取组分A的沸点 (x=0.0)
        
        返回:
        float - 组分A沸点 (°C)
        """
        return self.temps[0]
    
    def get_boiling_point_component_b(self):
        """
        获取组分B的沸点 (x=1.0)
        
        返回:
        float - 组分B沸点 (°C)
        """
        return self.temps[-1]
    
    def print_data_table(self):
        """
        打印完整的数据表
        """
        comp_a, comp_b = self.components
        print(f"{self.name}")
        print(f"{'Temp (℃)':<10} {'Vapor mole frac of ' + comp_a:<25} {'Liquid mole frac of ' + comp_a:<25} {'Relative volatility (α)':<25}")
        print("-" * 85)
        for point in self.data_points:
            temp = point["temp"]
            y = point["y"]
            x = point["x"]
            alpha = point.get("alpha")
            alpha_str = f"{alpha:.2f}" if alpha is not None else ""
            print(f"{temp:<10.1f} {y:<25.3f} {x:<25.3f} {alpha_str:<25}")


# 示例使用
if __name__ == "__main__":

    # 使用VLE类
    vle = VLE("/home/Grtresy/VSCodeRepository/ChemicalEngineeringToolkits/chemetk/data/methanol_water_vle.json")
    
    print(f"体系名称: {vle.name}")
    print(f"组分: {vle.components[0]} - {vle.components[1]}")
    print()
    
    # 示例查询
    x_test = 0.35
    properties = vle.get_all_properties_by_x(x_test)
    print(f"液相组成 x = {x_test}:")
    for key, value in properties.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n组分A沸点: {vle.get_boiling_point_component_a()} °C")
    print(f"组分B沸点: {vle.get_boiling_point_component_b()} °C")

    # print("\n完整数据表:")
    # vle.print_data_table()

    print(vle.get_alpha_by_x(0.5))