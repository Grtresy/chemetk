import os
import json
import hashlib
import pandas as pd
from pathlib import Path

# 定义缓存目录和索引文件路径
CACHE_DIR = Path(__file__).parent.parent / 'data' / 'nist'
INDEX_FILE = CACHE_DIR / 'nist_data_index.json'

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
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=4)

def get_cached_data(request_params):
    """
    尝试从缓存中获取数据。

    Args:
        request_params (dict): 定义请求的参数字典。

    Returns:
        pandas.DataFrame: 如果找到缓存则返回数据，否则返回None。
    """
    index = _load_index()
    request_hash = _get_request_hash(request_params)
    
    if request_hash in index:
        file_info = index[request_hash]
        filepath = CACHE_DIR / file_info['filename']
        if filepath.exists():
            print(f"从缓存加载数据: {filepath}")
            return pd.read_json(filepath, orient='split')
            
    return None

def cache_data(df, request_params):
    """
    将从NIST获取的数据缓存到本地。

    Args:
        df (pandas.DataFrame): 要缓存的数据。
        request_params (dict): 定义请求的参数字典。
    """
    index = _load_index()
    request_hash = _get_request_hash(request_params)
    
    filename = f"{request_hash}.json"
    filepath = CACHE_DIR / filename
    
    # 保存数据文件
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_json(filepath, orient='records', indent=4)
    
    # 更新并保存索引文件
    index[request_hash] = {
        'params': request_params,
        'filename': filename
    }
    _save_index(index)
    print(f"数据已缓存至: {filepath}")