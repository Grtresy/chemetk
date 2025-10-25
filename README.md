# cheme-toolkit

cheme-toolkit 是一个为化学工程计算设计的工具包，提供了气液平衡数据处理、精馏塔计算、热力学性质计算、可视化绘图以及 Web 应用等功能，方便化学工程相关的计算与模拟工作。

## 功能介绍

### 1. 气液平衡 (VLE) 数据处理
- 能够读取和解析 JSON 格式的气液平衡数据（例如 methanol_water_vle.json）。
- 核心类是 `chemetk.thermo.vle.VLE`，它加载数据后，可以根据液相组成 $x$ 插值计算出对应的气相组成 $y$、温度 $T$ 和相对挥发度 $\alpha$。
- 提供了一个数据文件管理器 (`chemetk.io.vle_data_manager.VLEDataManager`) 和便捷函数如 `chemetk.io.get_vle_file_path` 来自动发现和加载 `data` 目录下的 VLE 数据。

### 2. 精馏塔计算 (McCabe-Thiele 法)
- 核心类是 `chemetk.unit_ops.distillation.McCabeThiele`，它基于 `VLE` 数据进行逐板计算。
- 支持常规操作和全回流等多种模式。
- 能够计算理论塔板数（包括小数理论塔板数）并打印详细的计算结果摘要。

### 3. 热力学性质计算 (逸度)
- 可以从 NIST Webbook 获取指定物质在恒温下的 P-V-T 数据（使用 `chemetk.io.nist_webbook.fetch_isotherm_data`）。
- 能够根据 P-V 数据通过积分计算逸度（`fugacity`）和化学势（使用 `chemetk.thermo.fugacity.calculate_fugacity_from_pv_data`）。

### 4. 可视化绘图
- 提供了绘图功能，可以将 McCabe-Thiele 计算结果绘制成阶梯图（`chemetk.visualization.plotting.plot_mccabe_thiele`）。
- 也能将逸度和化学势的计算结果绘制成图表（`chemetk.visualization.plotting.plot_fugacity_results`）。

### 5. Web 应用
- 包含一个基于 Dash 的交互式 Web 应用 (chemetk/web/app.py)，用于在线模拟 McCabe-Thiele 精馏过程。用户可以在网页上输入参数并实时看到计算结果和图表。

## 使用范例

### 范例 1: McCabe-Thiele 精馏计算
这个例子展示了如何进行精馏塔的理论塔板数计算和绘图。

```python
from chemetk import VLE, McCabeThiele, plot_mccabe_thiele,VLEManager

vle_manager = VLEManager()

# 1. 定义问题参数
F, x_F = 100, 0.48
D, x_D = 49, 0.96
W, x_W = 51, 0.02
q = 1.0
R = 2.0

# 2. 加载VLE数据
# 使用io模块的函数获取数据文件路径
data_path = vle_manager.get_file_path_by_filename("methanol_water_vle")
vle = VLE(data_path=data_path)

# 3. 初始化McCabeThiele类
column = McCabeThiele(vle=vle, x_D=x_D, x_W=x_W, x_F=x_F, q=q, R=R, D=D, W=W, F=F)

# 4. 进行逐板计算
# 从塔顶开始计算，并返回小数理论塔板数
result_df, decimal_stages = column.calculate_stages(start_from='top', return_decimal_stages=True)

# 5. 打印计算结果摘要
column.print_summary(result_df, calculation_direction='top', decimal_stages=decimal_stages)

# 6. 绘制McCabe-Thiele图
fig = plot_mccabe_thiele(column, result_df)
fig.show()
```

### 范例 2: 计算二氧化碳的逸度和化学势
这个例子展示了如何从 NIST 获取数据，并计算逸度。

```python
from chemetk.io.nist_datamanager import fetch_isotherm_data
from chemetk.thermo.fugacity import calculate_fugacity_from_pv_data
from chemetk.visualization.plotting import plot_fugacity_results
import os

# --- 1. 获取数据 ---
T = 300.0  # K
fluid_name = 'CO₂'
fluid_id = 'C124389' # CO₂的NIST ID
df = fetch_isotherm_data(fluid_id=fluid_id, temp=T, p_low=0, p_high=5, p_inc=0.01)

# --- 2. 数据预处理 (省略) ---
# ...

# --- 3. 计算逸度和化学势 ---
pressures_mpa = df['Pressure (MPa)'].values
volumes_m3_mol = df['Volume (m3/mol)'].values
fugacities_mpa, chemical_potentials_kj_mol = calculate_fugacity_from_pv_data(
    pressures_mpa, volumes_m3_mol, T
)

# --- 4. 绘制图表 ---
fig, _ = plot_fugacity_results(
    pressures_mpa, 
    fugacities_mpa, 
    chemical_potentials_kj_mol,
    fluid_name=fluid_name,
    temp_k=T
)
# 保存图片
save_path = 'fugacity_chemical_potential_from_chemetk.png'
fig.savefig(save_path, dpi=300)
```

### 范例 3: 运行 Web 应用

您可以运行一个本地服务器来启动 McCabe-Thiele 模拟器。

```python
from chemetk.web.app import create_app

app = create_app()

if __name__ == '__main__':
    # 运行服务器
    # debug=True 可以在代码更改时自动重载
    app.run(debug=True, port=8050)
```

在终端中运行此脚本后，您可以在浏览器中打开 `http://127.0.0.1:8050` 来使用该工具。