'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-11-12 15:09:46
LastEditTime: 2024-12-30 11:36:16
FilePath: /tcl-check-of-dirty-api/src/api/routers/get_line.py
'''
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from src.api.setting import mapping # type: ignore
from src.database.clickhouse_connector import execute_query
import pandas as pd

class Item(BaseModel):
    time_selected: Optional[list] = []

router = APIRouter()

@router.post(f"/ai/check-of-dirty/line")
async def plot_data(item: Item):
    '''
    {
      code: 0,
      data: {
        xAxisData: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        line: [{
          name: '小白点',
          data: [110, 130, 124, 118, 135, 47, 160]
        },
        {
          name: '小白点1',
          data: [150, 230, 224, 218, 135, 147, 260]
        }]
      }
    }

    '''
    if pd.to_datetime(item.time_selected[1]) - pd.to_datetime(item.time_selected[0]) < pd.Timedelta(days=7):
        t1 = pd.to_datetime(item.time_selected[1]).strftime('%Y-%m-%d')
        t0 = (pd.to_datetime(item.time_selected[1]) - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
    else:
        t0 = pd.to_datetime(item.time_selected[0]).strftime('%Y-%m-%d')
        t1 = pd.to_datetime(item.time_selected[1]).strftime('%Y-%m-%d')
    
    sql = f'''
    select 
        *
    from 
        dip.im_dirt_discrimination 
    where 
        1=1
        and hy_date >= toDate('{t0}') 
        and hy_date < toDate('{t1}')
        and label is not null
        and label != ''
    '''
    df = execute_query(sql)
    df.rename(columns={'youw': 'youwu'}, inplace=True)
    if df.empty:
        return JSONResponse(content={"data": {}})
    
    df.hy_date = df.hy_date.map(lambda x: str(x).split(' ')[0])
    df = df.groupby('hy_date')[list(mapping.keys())].sum().reset_index()
    df['total'] = df[list(mapping.keys())].sum(axis=1)
    for key in list(mapping.keys()):
        df[key] = (df[key] / df['total']).round(2)
    df.drop(columns=['total'], inplace=True)
    
    data = dict()
    df.sort_values(by='hy_date', inplace=True)
    data['xAxisData'] = df.hy_date.tolist()
    data['line'] = []
    for key in mapping.keys():
        data['line'].append({
            'name': mapping.get(key, key),
            'data': df[key].tolist()
        })

    return JSONResponse(content={"data": data})