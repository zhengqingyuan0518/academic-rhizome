from app import create_app

app = create_app()

if __name__ == '__main__':
    # 启动Flask应用
    # debug=True 开启调试模式，修改代码后服务器会自动重启
    # port=5000 指定端口
    app.run(debug=True, port=5000)