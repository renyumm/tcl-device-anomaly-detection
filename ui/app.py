'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-12-17 10:52:33
LastEditTime: 2024-12-30 15:03:11
FilePath: /tcl-check-of-dirty-api/ui/app.py
'''

import threading
import socket
import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from tkinter import Tk, Label, Button, StringVar, Text, Scrollbar, END
import ctypes
import subprocess
import sys
import re  # 新增：用于正则表达式匹配

# 固定端口号
PORT = 18000

# FastAPI 应用
app = FastAPI()

# 目标服务器 URL (转发数据)
TARGET_URL = "http://10.225.214.14:31109"  # 可修改为实际目标地址
log_messages = []  # 存储日志信息

@app.post("/receive_data")
async def receive_data(request: Request):
    """
    接收 JSON 数据并转发到目标服务器
    """
    try:
        data = await request.json()
        log(f"Received data: {data}")

        # 转发数据到目标服务器
        response = requests.post(TARGET_URL, json=data)
        log(f"Forwarded to {TARGET_URL} - Response: {response.status_code}, {response.text}")

        return {"status": "success", "response_code": response.status_code, "response_body": response.text}
    except Exception as e:
        log(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "running"}

# 获取基于网线的 IP 地址
def get_ethernet_ip():
    try:
        output = subprocess.check_output("ipconfig", encoding='utf-8', errors='ignore')
        ethernet_section = False
        ip_address = "127.0.0.1"  # 默认回退地址

        for line in output.splitlines():
            # 检测以太网适配器的开始
            if re.search(r"Ethernet adapter", line, re.IGNORECASE):
                ethernet_section = True
            elif ethernet_section:
                # 匹配 IPv4 地址行（考虑中英文）
                ipv4_match = re.search(r"IPv4 Address[.\s]*:\s*([\d\.]+)", line, re.IGNORECASE)
                if ipv4_match:
                    ip_address = ipv4_match.group(1)
                    break
                # 检测到新适配器或空行，结束以太网部分
                elif line.strip() == "" or re.search(r"adapter", line, re.IGNORECASE):
                    ethernet_section = False

        return ip_address
    except Exception as e:
        log(f"获取以太网 IP 地址时出错: {str(e)}")
        return "127.0.0.1"  # 回退到本地地址

# 检查是否具有管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 打开指定端口的防火墙规则
def open_firewall_port(port):
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule",
             f"name=Open Port {port}", "dir=in", "action=allow",
             "protocol=TCP", f"localport={port}"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        log(f"Port {port} opened successfully!")
    except subprocess.CalledProcessError as e:
        log(f"Failed to open port {port}. Error: {e}")

# 日志记录
def log(message):
    log_messages.append(message)
    if gui:
        gui.update_logs()

# API 服务线程
def start_api_server():
    uvicorn.run(app, host="0.0.0.0", port=PORT)

# GUI 界面
class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("API Service Controller")
        self.is_running = False
        self.server_thread = None

        # IP 和端口显示
        ethernet_ip = get_ethernet_ip()
        self.ip_var = StringVar(value=f"Ethernet IP Address: {ethernet_ip}")
        self.port_var = StringVar(value=f"Port: {PORT}")

        Label(root, text="API Service Controller", font=("Arial", 16)).pack(pady=10)
        Label(root, textvariable=self.ip_var, font=("Arial", 12)).pack(pady=5)
        Label(root, textvariable=self.port_var, font=("Arial", 12)).pack(pady=5)

        # 启动和停止按钮
        self.start_button = Button(root, text="Start API Server", font=("Arial", 12), command=self.start_server)
        self.start_button.pack(pady=10)

        self.stop_button = Button(root, text="Stop API Server", font=("Arial", 12), command=self.stop_server, state="disabled")
        self.stop_button.pack(pady=10)

        # 日志显示
        Label(root, text="Logs:", font=("Arial", 12)).pack()
        self.log_text = Text(root, wrap="word", height=15, width=60, state="disabled")
        self.log_text.pack()
        scrollbar = Scrollbar(root, command=self.log_text.yview)
        self.log_text['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side="right", fill="y")

    def update_logs(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, END)
        self.log_text.insert(END, "\n".join(log_messages))
        self.log_text.config(state="disabled")

    def start_server(self):
        if not self.is_running:
            open_firewall_port(PORT)  # 打开 18000 端口
            self.is_running = True
            self.server_thread = threading.Thread(target=start_api_server, daemon=True)
            self.server_thread.start()
            log(f"API server started on port {PORT}")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

    def stop_server(self):
        # 停止服务（需手动关闭程序）
        log("Please restart the application to stop the server.")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

# 主函数
if __name__ == "__main__":
    if not is_admin():
        # 以管理员权限重新运行程序
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

    # 启动 GUI
    root = Tk()
    gui = AppGUI(root)
    root.mainloop()
