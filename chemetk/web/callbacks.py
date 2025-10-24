from dash.dependencies import Input, Output, State
from chemetk.thermo import vle
from chemetk.unit_ops.distillation import McCabeThiele
from chemetk.visualization.plotly_plotting import create_distillation_plot_plotly
import pandas as pd
import plotly.graph_objects as go

def register_callbacks(app, vle_obj):
    """注册应用的所有回调函数"""

    @app.callback(
        Output('problem-definition-store', 'data'),
        [Input('input-F', 'value'),
         Input('input-xF', 'value'),
         Input('input-xD', 'value'),
         Input('input-xW', 'value')]
    )
    def update_problem_definition(F, xF, xD, xW):
        """当基础参数输入改变时，更新 dcc.Store"""
        return {'F': F, 'xF': xF, 'xD': xD, 'xW': xW}

    @app.callback(
        Output('mccabe-thiele-graph', 'figure'),
        [Input('q-slider', 'value'),
         Input('R-slider', 'value'),
         Input('problem-definition-store', 'data')]
    )
    def update_graph(q_value, r_value, problem_data):
        """当滑块值或基础参数改变时，更新 McCabe-Thiele 图"""
        if not problem_data:
            return go.Figure()

        # 从 dcc.Store 中获取问题定义
        F = problem_data['F']
        x_D = problem_data['xD']
        x_W = problem_data['xW']
        x_F = problem_data['xF']
        
        # 计算D和W
        if F is not None and x_F is not None and x_D is not None and x_W is not None and x_D != x_W:
            D = F * (x_F - x_W) / (x_D - x_W)
            W = F - D
        else:
            D, W = 0, 0

        # 实例化 McCabeThiele
        column = McCabeThiele(
            vle=vle_obj,
            x_D=x_D,
            x_W=x_W,
            x_F=x_F,
            q=q_value,
            R=r_value,
            D=D,
            F=F,
            W=W
        )

        # 计算理论塔板数
        try:
            column.calculate_stages()
            plot_stages_flag = True
        except Exception:
            # 如果计算失败（例如最小回流比），则不绘制塔板
            plot_stages_flag = False

        # 生成图表
        fig = create_distillation_plot_plotly(
            mt_instance=column,
            plot_stages=plot_stages_flag,
            title=f"McCabe-Thiele (q={q_value:.1f}, R={r_value:.1f})"
        )
        return fig

    @app.callback(
        Output('q-slider-output', 'children'),
        [Input('q-slider', 'value')]
    )
    def update_q_slider_output(value):
        return f'当前值: {value:.1f}'

    @app.callback(
        Output('R-slider-output', 'children'),
        [Input('R-slider', 'value')]
    )
    def update_R_slider_output(value):
        return f'当前值: {value:.1f}'

    # @app.callback(
    #     Output('distillation-graph', 'figure'), # 假设你的 dcc.Graph 组件的 id 是 'distillation-graph'
    #     [Input('calculate-button', 'n_clicks')], # 假设有一个触发计算的按钮
    #     [State('some-input', 'value'),] # ...以及其他输入参数
    # )
    # def update_distillation_graph(n_clicks, some_input_value):
    #     if n_clicks is None:
    #         # 页面刚加载时，不执行计算，可以返回一个空的 figure
    #         return go.Figure()

    #     # 1. 在这里执行你的蒸馏计算
    #     # ... 得到计算结果，例如 stages_df, eq_line_df, op_line_df
    #     # 以下是示例数据，你需要用你的真实计算结果替换
    #     stages_df = pd.DataFrame({'x': [0.8, 0.8, 0.6, 0.6, 0.3, 0.3], 'y': [0.8, 0.7, 0.7, 0.5, 0.5, 0.2]})
    #     eq_line_df = pd.DataFrame({'x': [0, 0.2, 0.4, 0.6, 0.8, 1.0], 'y': [0, 0.35, 0.55, 0.7, 0.8, 1.0]})
    #     op_line_df = pd.DataFrame({
    #         'x': [0.3, 0.9], 
    #         'y': [0.4, 0.85], 
    #         'line_name': ['精馏段操作线', '精馏段操作线']
    #     })


    #     # 2. 调用新的 Plotly 绘图函数
    #     fig = create_distillation_plot_plotly(stages_df, eq_line_df, op_line_df)

    #     # 3. 返回 Plotly figure 对象
    #     return fig