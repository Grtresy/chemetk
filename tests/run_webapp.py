from chemetk.web.app import create_app

app = create_app()

if __name__ == '__main__':
    # 运行服务器
    # debug=True 可以在代码更改时自动重载
    app.run(debug=False,port=8050)

