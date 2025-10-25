import dash
from chemetk.thermo.vle import VLE
from chemetk.io.vle_datamanager import VLEManager
from .layout import create_layout
from .callbacks import register_callbacks

def create_app():
    """创建并配置Dash应用实例"""
    # 加载VLE数据
    vle_manager = VLEManager()
    data_path = vle_manager.get_file_path_by_filename("methanol_water_vle")
    if not data_path:
        raise FileNotFoundError("未找到 VLE 数据文件 'methanol_water_vle.json'")
    vle = VLE(data_path=data_path)

    # 创建Dash app
    app = dash.Dash(__name__)
    app.title = "McCabe-Thiele Simulator"

    # 设置布局
    app.layout = create_layout()

    # 注册回调
    register_callbacks(app, vle)

    return app