from dash import dcc, html

def create_layout():
    """创建应用的布局 (优化版)"""
    return html.Div([
        # 1. 存储组件，用于在回调间传递数据（保留）
        dcc.Store(id='problem-definition-store'),

        # 2. 页面标题
        html.Div([
            html.H1("McCabe-Thiele 精馏塔模拟器"),
            html.P("输入参数并计算理论塔板数。")
        ], className="header-container"),

        # 3. 主内容容器 (控制面板 + 输出面板)
        html.Div([
            
            # 3.1. 左侧控制面板 (使用 'card' 样式)
            html.Div([
                html.H3("输入参数"),

                # 将每个 Label-Input 组合包裹在 Div 中，便于样式控制
                html.Div([
                    html.Label("进料流率 (F)", htmlFor='input-F'),
                    dcc.Input(id='input-F', type='number', value=100, className="input-field"),
                ], className="parameter-group"),

                html.Div([
                    html.Label("进料组成 (xF)", htmlFor='input-xF'),
                    dcc.Input(id='input-xF', type='number', value=0.5, min=0, max=1, step=0.01, className="input-field"),
                ], className="parameter-group"),
                
                html.Div([
                    html.Label("塔顶产品组成 (xD)", htmlFor='input-xD'),
                    dcc.Input(id='input-xD', type='number', value=0.95, min=0, max=1, step=0.01, className="input-field"),
                ], className="parameter-group"),

                html.Div([
                    html.Label("塔底产品组成 (xW)", htmlFor='input-xW'),
                    dcc.Input(id='input-xW', type='number', value=0.05, min=0, max=1, step=0.01, className="input-field"),
                ], className="parameter-group"),

                # 优化的滑块布局
                html.Div([
                    # 将标签和数值显示在同一行
                    html.Div([
                        html.Label("进料热状态 (q)", htmlFor='q-slider'),
                        html.Span(id='q-slider-output', style={'fontWeight': 'bold'}), # 使用 Span 在行内显示
                    ], className="slider-label-row"),
                    dcc.Slider(id='q-slider', min=-0.5, max=1.5, step=0.1, value=1.0, marks={i/10: str(i/10) for i in range(-5, 16, 5)}),
                ], className="parameter-group slider-group"),

                # 优化的滑块布局
                html.Div([
                    # 将标签和数值显示在同一行
                    html.Div([
                        html.Label("回流比 (R)", htmlFor='R-slider'),
                        html.Span(id='R-slider-output', style={'fontWeight': 'bold'}), # 使用 Span 在行内显示
                    ], className="slider-label-row"),
                    dcc.Slider(id='R-slider', min=0.1, max=4.0, step=0.1, value=2.5, marks={i: str(i) for i in range(0, 5)}), # 简化 marks
                ], className="parameter-group slider-group"),

                # 添加一个明确的计算按钮
                html.Button('开始计算', id='run-simulation-button', n_clicks=0, className='run-button'),

            ], className="control-panel card-style"), # 添加 'card-style'

            # 3.2. 右侧图表和结果 (使用 'card' 样式)
            html.Div([
                dcc.Graph(id='mccabe-thiele-graph', style={'height': '60vh'}), # 给予图表一个初始高度
                html.Hr(), # 添加分割线
                html.H3("计算结果"),
                html.Div(id='output-results', className="results-container")
            ], className="output-panel card-style") # 添加 'card-style'

        ], className="main-container"),
    ])