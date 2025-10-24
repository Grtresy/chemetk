from dash import dcc, html

def create_layout():
    """创建应用的布局"""
    return html.Div([
        # 在布局的顶层添加 dcc.Store 组件
        dcc.Store(id='problem-definition-store'),

        html.H1("McCabe-Thiele 精馏塔模拟器"),

        html.Div([
            # 左侧控制面板
            html.Div([
                html.H3("输入参数"),
                
                html.Label("进料流率 (F)"),
                dcc.Input(id='input-F', type='number', value=100, className="input-field"),
                
                html.Label("进料组成 (xF)"),
                dcc.Input(id='input-xF', type='number', value=0.5, min=0, max=1, step=0.01, className="input-field"),
                
                html.Label("塔顶产品组成 (xD)"),
                dcc.Input(id='input-xD', type='number', value=0.95, min=0, max=1, step=0.01, className="input-field"),
                
                html.Label("塔底产品组成 (xW)"),
                dcc.Input(id='input-xW', type='number', value=0.05, min=0, max=1, step=0.01, className="input-field"),

                html.Label("进料热状态 (q)"),
                dcc.Slider(id='q-slider', min=-0.5, max=1.5, step=0.1, value=1.0, marks={i/10: str(i/10) for i in range(-5, 16, 5)}),
                html.Div(id='q-slider-output', style={'textAlign': 'center', 'padding': '5px'}),

                html.Label("回流比 (R)"),
                dcc.Slider(id='R-slider', min=0.1, max=4.0, step=0.1, value=2.5, marks={i: str(i) for i in range(0, 41)}),
                html.Div(id='R-slider-output', style={'textAlign': 'center', 'padding': '5px'}),

            ], className="control-panel"),

            # 右侧图表和结果
            html.Div([
                dcc.Graph(id='mccabe-thiele-graph'),
                html.Div(id='output-results')
            ], className="output-panel")
        ], className="main-container"),
    ])