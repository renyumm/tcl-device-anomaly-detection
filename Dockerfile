FROM python:3.11

# 定义构建参数并设定默认值
ARG FACTORY
# 设置运行时环境变量
ENV FACTORY=${FACTORY}

# 设置工作目录
WORKDIR /tcl-influence-of-accessories

# 复制 requirements.txt 文件到工作目录
COPY requirements.txt ./
# 安装 Python 依赖包
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 复制项目文件到工作目录
COPY src ./src/

# 运行应用（根据你的项目入口文件调整） 
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2"]
