# chemetk/visualization/plotting.py

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

from ..unit_ops.distillation import McCabeThiele

def plot_vle_txy(vle, title: Optional[str] = None, show: bool = True):
    """
    绘制二元体系的温度-组成图 (T-x-y diagram)。

    :param vle: VLE 类的实例，包含汽液平衡数据和插值方法。
    :param title: 图表标题。如果为 None，则使用 VLE 数据中的名称。
    :param show: 是否立即显示图像。
    """
    # 生成平滑的曲线数据
    x_continuous = np.linspace(0.0, 1.0, 200)
    y_continuous = vle.get_y_by_x(x_continuous)
    temp_continuous_x = vle.get_temperature_by_x(x_continuous)
    temp_continuous_y = vle.get_temperature_by_y(y_continuous)

    plt.figure(figsize=(10, 7))
    
    # 绘制泡点线 (T-x)
    plt.plot(x_continuous, temp_continuous_x, 'b-', linewidth=2, label='Bubble point line (T-x)')
    # 绘制露点线 (T-y)
    plt.plot(y_continuous, temp_continuous_y, 'r-', linewidth=2, label='Dew point line (T-y)')
    
    # 绘制原始数据点
    plt.plot(vle.x_values, vle.temps, 'bo', label='Bubble point data')
    plt.plot(vle.y_values, vle.temps, 'ro', label='Dew point data')

    # 设置图表标题和标签
    if title is None:
        title = f'{vle.name} T-x-y Diagram (101.3kPa)'
    
    comp_a = vle.components[0]
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(f'Mole Fraction of {comp_a} (x, y)', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.xlim(0.0, 1.0)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    if show:
        plt.tight_layout()
        plt.show()

def plot_vle_yx(vle, title: Optional[str] = None, show: bool = True):
    """
    绘制二元体系的汽液平衡图 (y-x diagram)。

    :param vle: VLE 类的实例。
    :param title: 图表标题。如果为 None，则使用 VLE 数据中的名称。
    :param show: 是否立即显示图像。
    """
    x_continuous = np.linspace(0.0, 1.0, 200)
    y_continuous = vle.get_y_by_x(x_continuous)

    plt.figure(figsize=(8, 8))
    
    # 绘制平衡线 (y-x)
    plt.plot(x_continuous, y_continuous, 'g-', linewidth=2, label='Equilibrium line (y-x)')
    # 绘制对角线 (y=x)
    plt.plot([0.0, 1.0], [0.0, 1.0], 'k--', linewidth=1.5, label='Diagonal line (y=x)')
    
    # 绘制原始数据点
    plt.plot(vle.x_values, vle.y_values, 'go', label='Equilibrium data')

    # 设置图表标题和标签
    if title is None:
        title = f'{vle.name} y-x Diagram (101.3kPa)'
        
    comp_a = vle.components[0]
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(f'Liquid Mole Fraction of {comp_a} (x)', fontsize=12)
    plt.ylabel(f'Vapor Mole Fraction of {comp_a} (y)', fontsize=12)
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1.0)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.gca().set_aspect('equal', adjustable='box')
    
    if show:
        plt.tight_layout()
        plt.show()

from ..unit_ops.distillation import McCabeThiele

def plot_mccabe_thiele(mt_instance: McCabeThiele, plot_stages: bool = True, 
                                      title: Optional[str] = None, show: bool = True):
    """
    使用 Matplotlib 创建精馏塔的 McCabe-Thiele 图。

    参数:
    - mt_instance: McCabeThiele 类的实例
    - plot_stages (bool): 是否绘制理论塔板的梯级图
    - title (Optional[str]): 图表标题
    - show (bool): 是否立即显示图表

    返回:
    - tuple: (fig, ax) Matplotlib 图形和坐标轴对象
    """
    # 创建图形和坐标轴
    fig, ax = plt.subplots(figsize=(10, 10))
    vle = mt_instance.vle
    x_D, x_W, x_F, q = mt_instance.x_D, mt_instance.x_W, mt_instance.x_F, mt_instance.q

    # 1. 准备平衡线数据
    x_eq = np.linspace(0.0, 1.0, 200)
    y_eq = vle.get_y_by_x(x_eq)
    
    # 绘制平衡线
    ax.plot(x_eq, y_eq, 'b-', label='Equilibrium Line', linewidth=2)

    # 绘制对角线 (y=x)
    ax.plot([0, 1], [0, 1], '--', color='grey', label='y=x', linewidth=1.5)

    # 2. 准备并绘制操作线
    # 计算三条线的交点
    if q == 1:
        x_int = x_F
        y_int = mt_instance.L_over_V * x_int + mt_instance.D_xD_over_V
    elif q == 0:
        y_int = x_F
        x_int = (y_int - mt_instance.D_xD_over_V) / mt_instance.L_over_V
    else:
        x_int = (mt_instance.D_xD_over_V + x_F/(q-1)) / (q/(q-1) - mt_instance.L_over_V)
        y_int = mt_instance.L_over_V * x_int + mt_instance.D_xD_over_V
    
    # 精馏段操作线
    ax.plot([x_D, x_int], [x_D, y_int], 'b-', label='Rectifying Section', linewidth=2)
    # 提馏段操作线
    ax.plot([x_W, x_int], [x_W, y_int], 'r-', label='Stripping Section', linewidth=2)
    # q线
    ax.plot([x_F, x_int], [x_F, y_int], 'purple', linestyle='--', label='q-line', linewidth=1.5)

    # 3. 准备并绘制理论塔板阶梯
    if plot_stages:
        stages_df = mt_instance.calculate_stages(start_from="top")
        stage_x = []
        stage_y = []

        # 假设 stages_df 包含操作线上的点
        if not stages_df.empty:
            # 添加第一个点，作为路径的起点
            stage_x.append(stages_df['x_liquid'].iloc[0])
            stage_y.append(stages_df['y_vapor'].iloc[0])

            for i in range(len(stages_df) - 1):
                x_start = stages_df['x_liquid'].iloc[i]
                y_start = stages_df['y_vapor'].iloc[i]
                x_end = stages_df['x_liquid'].iloc[i+1]
                y_end = stages_df['y_vapor'].iloc[i+1]

                # 路径: (x_start, y_start) -> (x_start, y_end) -> (x_end, y_end)
                # 顶点1: 垂直移动后的点
                stage_x.append(x_start)
                stage_y.append(y_end)
                
                # 顶点2: 水平移动后的点 (即下一个操作线上的点)
                stage_x.append(x_end)
                stage_y.append(y_end)

            # 添加最后一个点，作为路径的终点
            stage_x.append(stages_df['x_liquid'].iloc[-1])
            stage_y.append(stages_df['x_liquid'].iloc[-1])

        # 绘制阶梯线
        ax.plot(stage_x, stage_y, 'g-', label='Theoretical Stages', linewidth=1.5, alpha=0.7)
        
        # 添加塔板编号
        stage_numbers_x = stages_df['x_liquid'].iloc[:-1]
        stage_numbers_y = stages_df['y_vapor'].iloc[1:]
        for i, (x, y) in enumerate(zip(stage_numbers_x, stage_numbers_y)):
            ax.text(x, y, f" {i+1}", fontsize=8, verticalalignment='center',
                   horizontalalignment='left', color='darkgreen')

    # 4. 标记重要点
    ax.plot(x_D, x_D, 'bo', markersize=8, label=f'x_D={x_D:.3f}')
    ax.plot(x_W, x_W, 'ro', markersize=8, label=f'x_W={x_W:.3f}')
    ax.plot(x_F, x_F, 'o', color='purple', markersize=8, label=f'x_F={x_F:.3f}')

    # 5. 更新图表布局
    if title is None:
        title = f'McCabe-Thiele Diagram for {vle.name}'
    
    comp_a = vle.components[0]
    
    # 设置坐标轴
    ax.set_xlabel(f"Liquid Phase Mole Fraction ({comp_a}) (x)", fontsize=12)
    ax.set_ylabel(f"Vapor Phase Mole Fraction ({comp_a}) (y)", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # 设置坐标轴范围
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # 设置网格
    ax.grid(True, alpha=0.3)
    
    # 设置等比例
    ax.set_aspect('equal')
    
    # 添加图例
    ax.legend(loc='upper left', fontsize=10)

    # 如果要求显示，则显示图表
    if show:
        plt.tight_layout()
        plt.show()
    
    return fig, ax

    

def plot_fugacity_results(pressures, fugacities, chemical_potentials, fluid_name, temp_k):
    """
    绘制逸度和化学势随压力变化的图表。

    Args:
        pressures (array-like): 压力数据 (单位: MPa).
        fugacities (array-like): 逸度数据 (单位: MPa).
        chemical_potentials (array-like): 化学势数据 (单位: kJ/mol).
        fluid_name (str): 流体名称.
        temp_k (float): 温度 (单位: K).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Fugacity vs pressure
    ax1.plot(pressures, fugacities, 'b-', linewidth=2, label='Fugacity f')
    ax1.plot(pressures, pressures, 'r--', linewidth=1, label='Ideal gas (f=p)')
    ax1.set_xlabel('Pressure p (MPa)')
    ax1.set_ylabel('Fugacity f (MPa)')
    ax1.set_title(f'{fluid_name} Fugacity vs Pressure (T={temp_k}K)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Chemical potential vs pressure
    ax2.plot(pressures, chemical_potentials, 'g-', linewidth=2)
    ax2.set_xlabel('Pressure p (MPa)')
    ax2.set_ylabel('Chemical potential μ (kJ/mol)')
    ax2.set_title(f'{fluid_name} Chemical Potential vs Pressure (T={temp_k}K)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig, (ax1, ax2)
