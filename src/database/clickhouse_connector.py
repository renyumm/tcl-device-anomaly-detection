'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-11-05 17:04:31
LastEditTime: 2025-01-14 11:30:20
FilePath: /tcl-check-of-dirty-api/src/database/clickhouse_connector.py
'''
from sqlalchemy import create_engine
import pandas as pd
import os
# 读取yaml文件, 从环境变量读取工厂号
import yaml
# 从环境变量获取工厂号
factory = os.getenv('FACTORY', 'dw5')

# 根据工厂号读取对应的配置文件
config_path = f'src/config/{factory}.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# 从配置文件中获取连接参数    
host = config['host']
port = config['port'] 
username = config['username']
password = config['password']
table_name = 'im_dirt_discrimination'

conn_str = f'clickhouse://{username}:{password}@{host}:{port}/dip'
engine = create_engine(conn_str)

def execute_query(query):
    df = pd.read_sql(query, engine)
    engine.dispose()

    return df

def insert_data(df):
    df.to_sql(table_name, engine, if_exists='append', index=False)


def query_runcard(query):
    host = '10.202.116.51'
    port = 21050
    username = 'hdfs'
    conn_str = f'impala://{username}@{host}:{port}'
    engine = create_engine(conn_str)
    df = pd.read_sql(query, engine)
    engine.dispose()

    return df
