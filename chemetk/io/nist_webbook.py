import requests
import pandas as pd
from io import StringIO
from . import nist_cache

def fetch_isotherm_data(fluid_id, temp, p_low, p_high, p_inc=0.1, t_unit='K', p_unit='MPa'):
    """
    从 NIST Webbook 获取指定流体的等温线物性数据。
    如果本地存在缓存，则从缓存加载数据。

    Args:
        fluid_id (str): 流体的NIST ID (例如, CO₂ 是 'C124389').
        temp (float): 温度.
        p_low (float): 压力下限.
        p_high (float): 压力上限.
        p_inc (float): 压力增量.
        t_unit (str): 温度单位 ('K', 'C', 'F', 'R').
        p_unit (str): 压力单位 ('MPa', 'bar', 'atm', 'kPa', 'Pa', 'psia').

    Returns:
        pandas.DataFrame: 包含物性数据的DataFrame，如果请求失败则返回None。
    """
    # 定义用于缓存的请求参数
    request_params = {
        'fluid_id': fluid_id,
        'temp': temp,
        'p_low': p_low,
        'p_high': p_high,
        'p_inc': p_inc,
        't_unit': t_unit,
        'p_unit': p_unit,
    }

    # 检查缓存
    cached_df = nist_cache.get_cached_data(request_params)
    if cached_df is not None:
        return cached_df

    print("本地未找到缓存，正在从NIST请求数据...")
    url = "https://webbook.nist.gov/cgi/fluid.cgi"
    params = {
        'Action': 'Data', 
        'Wide': 'on', 
        'ID': fluid_id, 
        'Type': 'IsoTherm',
        'Digits': '5', 
        'PLow': p_low, 
        'PHigh': p_high, 
        'PInc': p_inc,
        'T': temp, 
        'RefState': 'DEF', 
        'TUnit': t_unit, 
        'PUnit': p_unit,
        'DUnit': 'mol/m3', 
        'HUnit': 'kJ/mol', 
        'WUnit': 'm/s',
        'VisUnit': 'Pa*s', 
        'STUnit': 'N/m'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        lines = response.text.strip().split('\n')
        # 过滤掉注释行
        data_lines = [line for line in lines if not line.strip().startswith('#')]
        if not data_lines:
            print("警告: 未从NIST获取到有效数据行。")
            return None
        
        # 使用StringIO将文本数据读入pandas
        data_io = StringIO('\n'.join(data_lines))
        df = pd.read_csv(data_io, sep='\t')

        # 缓存数据
        nist_cache.cache_data(df, request_params)
        
        return df
    else:
        print(f"从NIST请求数据失败，状态码: {response.status_code}")
        return None