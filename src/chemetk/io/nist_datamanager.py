import json
import hashlib
import pandas as pd
import requests
from io import StringIO

from . import paths  # 导入统一的路径管理器

# 【修改】使用统一的 paths 模块获取可写目录
# 在用户数据目录下创建一个 'nist' 子目录来存放NIST缓存
CACHE_DIR = paths.get_user_data_dir() / 'nist'
INDEX_FILE = CACHE_DIR / 'nist_data_index.json'

# 确保缓存目录在模块加载时就存在
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _get_request_hash(params):
    """根据请求参数生成唯一的哈希值"""
    params_str = json.dumps(params, sort_keys=True)
    return hashlib.sha256(params_str.encode('utf-8')).hexdigest()

def _load_index():
    """加载缓存索引文件"""
    if not INDEX_FILE.exists():
        return {}
    with open(INDEX_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _save_index(index):
    """保存缓存索引文件"""
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=4)

def get_cached_data(request_params):
    """
    尝试从缓存中获取数据。
    """
    index = _load_index()
    request_hash = _get_request_hash(request_params)
    
    if request_hash in index:
        file_info = index[request_hash]
        filepath = CACHE_DIR / file_info['filename']
        if filepath.exists():
            print(f"从缓存加载数据: {filepath}")
            # 【修复】原始代码中保存和读取的 orient 不一致
            # 保存时用 'split'，读取时也用 'split'
            return pd.read_json(filepath, orient='split')
            
    return None

def cache_data(df, request_params):
    """
    将从NIST获取的数据缓存到本地。
    """
    index = _load_index()
    request_hash = _get_request_hash(request_params)
    
    filename = f"{request_hash}.json"
    filepath = CACHE_DIR / filename
    
    # 保存数据文件
    # 【修复】使用 'split' 格式，它比 'records' 更高效，且与 get_cached_data 匹配
    df.to_json(filepath, orient='split', indent=4)
    
    # 更新并保存索引文件
    index[request_hash] = {
        'params': request_params,
        'filename': filename
    }
    _save_index(index)
    print(f"数据已缓存至: {filepath}")

def fetch_isotherm_data(fluid_id, temp, p_low, p_high, p_inc=0.1, t_unit='K', p_unit='MPa'):
    """
    从 NIST Webbook 获取指定流体的等温线物性数据。
    如果本地存在缓存，则从缓存加载数据。
    
    ... (Args 和 Returns 不变) ...
    """
    request_params = {
        'fluid_id': fluid_id,
        'temp': temp,
        'p_low': p_low,
        'p_high': p_high,
        'p_inc': p_inc,
        't_unit': t_unit,
        'p_unit': p_unit,
    }

    # 检查缓存 (现在会调用 chemetk/io/cache.py 中的函数)
    cached_df = get_cached_data(request_params)
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
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            data_lines = [line for line in lines if not line.strip().startswith('#')]
            if not data_lines:
                print("警告: 未从NIST获取到有效数据行。")
                return None
            
            data_io = StringIO('\n'.join(data_lines))
            df = pd.read_csv(data_io, sep='\t')

            # 缓存数据
            cache_data(df, request_params)
            
            return df
        else:
            print(f"从NIST请求数据失败，状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        return None