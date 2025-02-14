'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-11-12 15:09:46
LastEditTime: 2025-02-14 10:36:50
FilePath: /tcl-check-of-dirty-api/src/api/routers/get_bar.py
'''
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from src.database.clickhouse_connector import query_runcard, execute_query
import os
import yaml
# 根据工厂号读取对应的配置文件
# 从环境变量获取工厂号
factory = os.getenv('FACTORY', 'dw5')
config_path = f'src/config/{factory}.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

table_name = config['table_name']

class Item(BaseModel):
    time_selected: Optional[list] = []

router = APIRouter()

@router.post(f"/ai/check-of-dirty/bar")
async def plot_data(item: Item):
    sql2 = f'''
    select 
        distinct eq_number
    from 
        dip.im_dirt_discrimination 
    where 
        1=1
        and hy_date >= toDate('{item.time_selected[0]}') 
        and hy_date < toDate('{item.time_selected[1]}')
        and label is not null
        and label != ''
    '''
    df2 = execute_query(sql2)
    df2 = df2.eq_number.tolist()
    df2 = [x for x in df2 if x != '']
    if factory in ['dw2', 'dw4']:
        machine_aoi = 'aoi'
        zb = 'aoi_field04'
        lp = 'lilun_piece'
        dtime = 'partition_date'
    elif factory == 'dw3':
        zb = 'aoi_b_grease_stains'
        lp = 'line_cutter_theoretical_cuts'
        dtime = 'machine_date_time'
    elif factory == 'dw5':
        zb = 'machine_dirty_b'
        lp = 'theoretical_wafer_quantity'
        dtime = 'machine_date_time'
    sql = f'''
        SELECT 
            t.{machine_aoi} as eq_number,
            sum(COALESCE(toFloat64(nullIf(t.{zb}, '')), 0))/sum(COALESCE(toFloat64(nullIf(t.{lp}, '')), 0)) as total
        FROM
            {table_name} t
        WHERE
            t.{dtime} >= '{item.time_selected[0].split(" ")[0]}'
            and t.{dtime} < '{item.time_selected[1].split(" ")[0]}'
        GROUP BY
            t.{machine_aoi}
        '''
    if factory != 'dw5':
        df = execute_query(sql)
    else:
        df = query_runcard(sql)
        
    if df.empty:
        return JSONResponse(content={"data": {}})

    df['test'] = df['eq_number']
    df['eq_number'] = df['eq_number'].map(lambda x: x[-3:])
    if df2:
        df = df[df.eq_number.isin(df2)]
    df.total = df.total.map(lambda x: round(x*100, 2))
    df.sort_values(by='total', inplace=True, ascending=False)
    df = df[:10]
    
    data = dict()
    data['xAxisData'] = df.eq_number.tolist()
    data['row'] = {
        'name': '柱状图',
        'data': df.total.tolist()
    }
    return JSONResponse(content={"data": data})