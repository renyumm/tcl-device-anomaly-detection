'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-11-12 15:09:46
LastEditTime: 2025-01-14 13:57:17
FilePath: /tcl-check-of-dirty-api/src/api/routers/get_pareto.py
'''
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from src.database.clickhouse_connector import execute_query
from src.api.setting import mapping # type: ignore

class Item(BaseModel):
    time_selected: Optional[list] = []

router = APIRouter()

@router.post(f"/ai/check-of-dirty/pareto")
async def plot_data(item: Item):
    '''
    {
      code: 0,
      data: {
        xAxisData: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        row: {
          name: '小白点',
          data: [110, 130, 124, 118, 135, 47, 160]
        },
        line: {
          name: '小白点1',
          data: [150, 230, 224, 218, 135, 147, 260]
        }
      }
    }

    '''
    sql = f'''
    select 
        label as name, 
        count(*) as value 
    from 
        dip.im_dirt_discrimination 
    where 
        1=1
        and hy_date >= toDate('{item.time_selected[0]}') 
        and hy_date < toDate('{item.time_selected[1]}')
        and label is not null
        and label != ''
    group 
        by label
    '''
    df = execute_query(sql)
    if df.empty:
        return JSONResponse(content={"data": {}})
    
    df['name'] = df['name'].apply(lambda x: mapping.get(x, x))
    df.sort_values(by='value', inplace=True, ascending=False)
    # 计算累计百分比
    df['cumsum'] = df['value'].cumsum()
    df['cumsum_percent'] = ((df['cumsum'] / df['value'].sum()) * 100).round(0)

    data = dict()
    data['xAxisData'] = df.name.tolist()
    data['row'] = {
        'name': '柱状图',
        'data': df.value.tolist()
    }
    data['line'] = {
        'name': '折线图',
        'data': df.cumsum_percent.tolist()  # 累计百分比
    }
    
    return JSONResponse(content={"data": data})