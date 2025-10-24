import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

# 假设 McCabeThiele 类在其他模块中定义
from ..unit_ops.distillation import McCabeThiele

def create_distillation_plot_plotly(mt_instance: McCabeThiele, plot_stages: bool = True, title: Optional[str] = None):
    """
    使用 Plotly 创建精馏塔的 McCabe-Thiele 图。

    参数:
    - mt_instance: McCabeThiele 类的实例。
    - plot_stages (bool): 是否绘制理论塔板的梯级图。
    - title (Optional[str]): 图表标题。

    返回:
    - go.Figure: 一个 Plotly Figure 对象。
    """
    fig = go.Figure()
    vle = mt_instance.vle
    x_D, x_W, x_F, q = mt_instance.x_D, mt_instance.x_W, mt_instance.x_F, mt_instance.q

    # 1. 准备平衡线数据
    x_eq = np.linspace(0.0, 1.0, 200)
    y_eq = vle.get_y_by_x(x_eq)
    
    # 绘制平衡线
    fig.add_trace(go.Scatter(
        x=x_eq, 
        y=y_eq,
        mode='lines',
        name='平衡线 (Equilibrium)',
        line=dict(color='blue')
    ))

    # 绘制对角线 (y=x)
    fig.add_trace(go.Scatter(
        x=[0, 1], 
        y=[0, 1],
        mode='lines',
        name='y=x',
        line=dict(color='gray', dash='dash')
    ))

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
    fig.add_trace(go.Scatter(x=[x_D, x_int], y=[x_D, y_int], mode='lines', name='精馏段操作线', line=dict(color='blue')))
    # 提馏段操作线
    fig.add_trace(go.Scatter(x=[x_W, x_int], y=[x_W, y_int], mode='lines', name='提馏段操作线', line=dict(color='red')))
    # q线
    fig.add_trace(go.Scatter(x=[x_F, x_int], y=[x_F, y_int], mode='lines', name='q线', line=dict(color='purple', dash='dash')))

    # 3. 准备并绘制理论塔板阶梯 (重构版本)
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

        fig.add_trace(go.Scatter(
            x=stage_x, 
            y=stage_y,
            mode='lines',
            name='理论塔板',
            line=dict(color='green')
        ))
        
        # 添加塔板编号，放在每个水平线的末端（即平衡线上的点）
        stage_numbers_x = stages_df['x_liquid'].iloc[:-1]
        stage_numbers_y = stages_df['y_vapor'].iloc[1:]
        fig.add_trace(go.Scatter(
            x=stage_numbers_x,
            y=stage_numbers_y,
            mode='text',
            text=[f" {s}" for s in stages_df['stage'].iloc[1:]],
            textposition='middle right',
            showlegend=False
        ))

    # 4. 标记重要点
    fig.add_trace(go.Scatter(x=[x_D], y=[x_D], mode='markers', name=f'x_D={x_D:.3f}', marker=dict(color='blue', size=8)))
    fig.add_trace(go.Scatter(x=[x_W], y=[x_W], mode='markers', name=f'x_W={x_W:.3f}', marker=dict(color='red', size=8)))
    fig.add_trace(go.Scatter(x=[x_F], y=[x_F], mode='markers', name=f'x_F={x_F:.3f}', marker=dict(color='purple', size=8)))

    # 5. 更新图表布局
    if title is None:
        title = f'McCabe-Thiele Diagram for {vle.name}'
    
    comp_a = vle.components[0]
    fig.update_layout(
        title=title,
        xaxis_title=f"液相摩尔分数 ({comp_a}) (x)",
        yaxis_title=f"气相摩尔分数 ({comp_a}) (y)",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1]),
        legend_title="图例",
        width=800,
        height=800,
        yaxis_scaleanchor="x",
        yaxis_scaleratio=1
    )
    
    return fig