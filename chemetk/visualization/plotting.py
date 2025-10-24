# chemetk/visualization/plotting.py

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

# 假设 VLE 和 McCabeThiele 类在其他模块中定义
# from ..thermo.vle import VLE
# from ..unit_ops.distillation import McCabeThiele

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

def plot_mccabe_thiele(mt_instance: McCabeThiele, plot_stages: bool = True, title: Optional[str] = None, show: bool = True):
    """
    绘制 McCabe-Thiele 图，包括平衡线、操作线和理论塔板。

    :param mt_instance: McCabeThiele 类的实例。
    :param plot_stages: 是否绘制理论塔板的梯级图。
    :param title: 图表标题。
    :param show: 是否立即显示图像。
    """
    vle = mt_instance.vle
    x_D, x_W, x_F, q = mt_instance.x_D, mt_instance.x_W, mt_instance.x_F, mt_instance.q
    
    plt.figure(figsize=(10, 10))
    
    # 1. 绘制平衡线和对角线
    x_continuous = np.linspace(0.0, 1.0, 200)
    y_continuous = vle.get_y_by_x(x_continuous)
    plt.plot(x_continuous, y_continuous, 'g-', linewidth=2, label='Equilibrium line (y-x)')
    plt.plot([0.0, 1.0], [0.0, 1.0], 'k--', linewidth=1, label='Diagonal line (y=x)')

    # 2. 绘制操作线

    # 计算三条线的交点
    if q == 1:
        # q线为垂直线 x = x_F
        x_int = x_F
        y_int = mt_instance.L_over_V * x_int + mt_instance.D_xD_over_V
    elif q == 0:
        # q线为水平线 y = x_F
        y_int = x_F
        x_int = (y_int - mt_instance.D_xD_over_V) / mt_instance.L_over_V
    else:
        # 计算精馏段操作线与q线的交点
        # 精馏段操作线: y = L_over_V * x + D_xD_over_V
        # q线: y = q/(q-1) * x - x_F/(q-1)
        # 联立求解
        x_int = (mt_instance.D_xD_over_V + x_F/(q-1)) / (q/(q-1) - mt_instance.L_over_V)
        y_int = mt_instance.L_over_V * x_int + mt_instance.D_xD_over_V

    # 精馏段操作线：从对角线(x_D, x_D)到交点(x_int, y_int)
    plt.plot([x_D, x_int], [x_D, y_int], 'b-', linewidth=2, label='Rectifying section OL')
    
    # 提馏段操作线：从对角线(x_W, x_W)到交点(x_int, y_int)
    plt.plot([x_W, x_int], [x_W, y_int], 'r-', linewidth=2, label='Stripping section OL')
    
    # q线：从对角线(x_F, x_F)到交点(x_int, y_int)
    plt.plot([x_F, x_int], [x_F, y_int], 'm--', linewidth=2, label='q-line')
    # 保存交点坐标到mt_instance中供后续使用
    mt_instance.intersection_point = (x_int, y_int)

    # # 精馏段操作线
    # x_rectifying = np.linspace(x_F, x_D, 100)
    # y_rectifying = mt_instance.L_over_V * x_rectifying + mt_instance.D_xD_over_V
    # plt.plot(x_rectifying, y_rectifying, 'b-', label='Rectifying section OL')

    # # 提馏段操作线
    # x_stripping = np.linspace(x_W, x_F, 100)
    # y_stripping = mt_instance.L_prime_over_V_prime * x_stripping - mt_instance.W_xW_over_V_prime
    # plt.plot(x_stripping, y_stripping, 'r-', label='Stripping section OL')

    # # q线
    # if q == 1:
    #     plt.plot([x_F, x_F], [x_F, vle.get_y_by_x(x_F)], 'm--', label='q-line (Saturated liquid)')
    # elif q == 0:
    #     plt.plot([x_F, vle.get_x_by_y(x_F)], [x_F, x_F], 'm--', label='q-line (Saturated vapor)')
    # else:
    #     y_intersect = mt_instance.L_over_V * x_F + mt_instance.D_xD_over_V
    #     plt.plot([x_F, (y_intersect - (q / (q - 1)) * x_F) / (1 - q / (q - 1))], [y_intersect, y_intersect - (q / (q - 1)) * (y_intersect - x_F)], 'm--', label='q-line')

    # 3. 绘制理论塔板梯级
    # if plot_stages:
    #     stages_df = mt_instance.calculate_stages(start_from='top', murphree_efficiency=1.0)
    #     for i in range(len(stages_df) - 1):
    #         x1 = stages_df['x_liquid'].iloc[i]
    #         y1 = stages_df['y_vapor'].iloc[i]
    #         x2 = stages_df['x_liquid'].iloc[i+1]
    #         y2 = stages_df['y_vapor'].iloc[i+1]
            
    #         # 水平线: (x_n, y_n) -> (x_{n+1}, y_n)
    #         plt.plot([x1, x2], [y1, y1], 'k-', alpha=0.7)
    #         # 垂直线: (x_{n+1}, y_n) -> (x_{n+1}, y_{n+1})
    #         plt.plot([x2, x2], [y1, y2], 'k-', alpha=0.7)
    #     # 标记塔板号
    #     for i, row in stages_df.iterrows():
    #         plt.text(row['x_liquid'], row['y_vapor'], str(row['stage']), fontsize=8, ha='center', va='bottom')
    if plot_stages:
        stages_df = mt_instance.calculate_stages(start_from='top', murphree_efficiency=1.0)
        
        # 简单的修正：确保阶梯在平衡线和操作线之间
        for i in range(len(stages_df)):
            x = stages_df['x_liquid'].iloc[i]
            y = stages_df['y_vapor'].iloc[i]
            
            if i == 0:
                # 第一块板：从操作线开始
                # 假设你知道塔顶组成 xD
                x_prev = stages_df['x_liquid'].iloc[0]  # 需要替换为你的塔顶液相组成
                y_prev = stages_df['y_vapor'].iloc[0]  # 需要替换为你的塔顶气相组成（对于全凝器，yD = xD）
            else:
                # 使用前一块板的平衡点
                x_prev = stages_df['x_liquid'].iloc[i-1]
                y_prev = stages_df['y_vapor'].iloc[i-1]
            
            # 绘制阶梯
            # 水平线
            plt.plot([x_prev, x], [y_prev, y_prev], 'k-', alpha=0.7)
            # 垂直线  
            plt.plot([x, x], [y_prev, y], 'k-', alpha=0.7)
        
        # 标记塔板号
        for i, row in stages_df.iterrows():
            plt.text(row['x_liquid'], row['y_vapor'], str(row['stage']), 
                    fontsize=8, ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

    # 4. 标记重要点
    plt.plot(x_D, x_D, 'bo', markersize=8, label=f'$x_D={x_D:.3f}$')
    plt.plot(x_W, x_W, 'ro', markersize=8, label=f'$x_W={x_W:.3f}$')
    plt.plot(x_F, x_F, 'mo', markersize=8, label=f'$x_F={x_F:.3f}$')

    # 5. 设置图表样式
    if title is None:
        title = f'McCabe-Thiele Diagram for {vle.name}'
    
    comp_a = vle.components[0]
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(f'Liquid Mole Fraction of {comp_a} (x)', fontsize=12)
    plt.ylabel(f'Vapor Mole Fraction of {comp_a} (y)', fontsize=12)
    plt.xlim(min(0.0,x_int-0.05), 1.0)
    plt.ylim(min(0.0,y_int-0.05), 1.0)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.gca().set_aspect('equal', adjustable='box')
    
    if show:
        plt.tight_layout()
        plt.show()

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
