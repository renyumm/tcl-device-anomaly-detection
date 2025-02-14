'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-11-12 15:09:46
LastEditTime: 2025-02-11 16:38:08
FilePath: /tcl-check-of-dirty-api/src/api/routers/parse_data.py
'''
from fastapi import APIRouter, Request
from kafka import KafkaProducer
from kafka.errors import KafkaError
import pandas as pd
from src.database.clickhouse_connector import insert_data
import json
import re
from datetime import datetime
import uuid
import yaml
import os
factory = os.getenv('FACTORY', 'dw5')
config_path = f'src/config/{factory}.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

alert_flag = config['alert_flag']
# {'data_entity': {'cutting_number': 'FXR02P295241007Y01004', 'eq_number': '', 'hy_date': '2024-12-25 09:07:34', 'ganshuiyin': 23, 'huahen': 17, 'pianchiyin': 50, 'pidaiyin': 8, 'shishuiyin': 3, 'suizha': 2, 'wupan': 17, 'xiaobaidian': 2, 'xiaoheidian': 16, 'yanghua': 0, 'youw': 12, 'class1': 0, 'class2': 0, 'class3': 0, 'class4': 0, 'class5': 0, 'label': 'pianchiyin'}, 'flag': 0, 'machineId': 'B06'}
# {'alert_data': {'alert_info': '报警等级：low\nN0240929-RA1-0027-3单刀脏污大于50片,占比最大脏污类型为: 干水印，占比为:15%\n排查：槽体水质洁净度、槽体液位、槽体泡沫情况、溢流是否正常;处理建议：排查出异常处理并进行漂洗槽体换水', 'alert_level': 'low'}, 'flag': 1, 'machineId': 'B06'}

router = APIRouter()

@router.post(f"/ai/check-of-dirty/receive_data")
async def receive_data(request: Request):
    """
    接收 JSON 数据并转发到目标服务器
    """
    data = await request.json()
    print(f"Receive data: {data}")
    if data['flag'] == 0:
        data_entity = data['data_entity']
        data_entity['eq_number'] = data['machineId']
        df = pd.DataFrame([data_entity])
        insert_data(df)
        print(f"Insert data to clickhouse successfully: {data_entity}")
        
        return f"Insert data to clickhouse successfully: {data_entity}"
    
    elif str(data['flag']) == '1':
        input_str = data['alert_data']['alert_info']
        machineId = data['machineId']
        machineType = 'AOI'
        # 获取当前时间戳加长
        
        buildId = str(uuid.uuid4()).replace('-', '')
        # 获取当前时间
        sendTime = (datetime.now() + pd.Timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')

        # 分割字符串为行
        lines = input_str.split('\n')

        # 提取报警等级
        报警等级_match = re.match(r'报警等级[:：]\s*(\w+)', lines[0])
        报警等级 = 报警等级_match.group(1) if 报警等级_match else ""

        # 提取描述
        描述 = lines[1].strip()

        # 提取排查和处理建议
        后两行 = lines[2]
        # 使用分号分割
        parts = 后两行.split(';')
        排查 = ""
        处理建议 = ""

        for part in parts:
            if part.startswith('排查'):
                排查_match = re.match(r'排查[:：]\s*(.+)', part)
                排查 = 排查_match.group(1).strip() if 排查_match else ""
            elif part.startswith('处理建议'):
                处理建议_match = re.match(r'处理建议[:：]\s*(.+)', part)
                处理建议 = 处理建议_match.group(1).strip() if 处理建议_match else ""
        
        topic = 'ams.esblog.testx.sc.ec'
        switch_servers = {  
            'dw5': '10.225.212.128:9092',
            'dw3': '10.171.203.120:9092',
            'dw4': '10.202.111.98:9092',
            'dw2': '10.182.212.216:9092'
        }
        bootstrap_servers = switch_servers[factory]

        eclist = data.get('ecSender', ['05200033', '51230544'])
        if '26240048' in eclist:
            eclist.remove('26240048')

        # 构建字典
        alert_data = {
            "alarmLevel": 报警等级,
            "description": 描述,
            "investigate": 排查,
            "suggestion": 处理建议,
            "ecSender": eclist,
            "machineCode": machineId,
            "machineType": machineType,
            "buildId": buildId,
            "sendTime": sendTime
        }

        def json_serializer(data):
            """
            将 Python 字典序列化为 JSON 字符串，并编码为 UTF-8 字节流。
            """
            return json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8')

        kafka_config = {
            'bootstrap_servers': bootstrap_servers
        }

        producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_serializer=json_serializer,
            retries=5,       # 配置重试次数
            acks='all',      # 确保所有副本都确认消息
            linger_ms=10     # 延迟发送以批量发送消息
        )

        future = producer.send(topic, value=alert_data)
        try:
            record_metadata = future.get(timeout=10)  # 阻塞等待发送结果，设置超时时间为10秒
            print(f"消息成功发送到主题 {record_metadata.topic} 分区 {record_metadata.partition} 偏移量 {record_metadata.offset}")
        except KafkaError as e:
            print(f"发送消息时遇到 Kafka 错误: {e}")
        except Exception as e:
            print(f"发送消息时出错: {e}")
        else:
            print(f"Insert data to kafka successfully: {alert_data}")
            return f"Insert data to kafka successfully: {alert_data}"
