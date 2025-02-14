'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-11-12 15:09:46
LastEditTime: 2024-12-30 15:43:52
FilePath: /tcl-check-of-dirty-api/src/api/routers/get_pie.py
'''
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from src.database.clickhouse_connector import execute_query
from src.api.setting import mapping # type: ignore  

class Item(BaseModel):
    time_selected: Optional[list] = []
    xqeq_code: Optional[str] = ''

router = APIRouter()

@router.post(f"/ai/check-of-dirty/pie")
async def plot_data(item: Item):
    if item.xqeq_code != '':
        sql = f'''
        select 
            label as name, 
            count(*) as value 
        from 
            dip.im_dirt_discrimination 
        where 
            1=1
            and eq_number = '{item.xqeq_code}' 
            and hy_date >= toDate('{item.time_selected[0]}') 
            and hy_date < toDate('{item.time_selected[1]}')
            and label is not null
            and label != ''
        group 
            by label
        '''
    else:
        sql = f'''
        select 
            label as name, 
            count(*) as value 
        from 
            dip.im_dirt_discrimination 
        where 
            1=1
            and hy_date >= toDate('{item.time_selected[0]}') 
            and hy_date <= toDate('{item.time_selected[1]}')
            and label is not null
            and label != ''
        group 
            by label
        '''
    
    df = execute_query(sql)
    if df.empty:
        return JSONResponse(content={"data": {}})
    
    df['name'] = df['name'].apply(lambda x: mapping.get(x, x))
    # 显示占总量百分比
    df['value'] = df['value'].apply(lambda x: f"{round(x *100 / df['value'].sum(), 1)}")
    data = df.to_dict(orient='records') 
    
    return JSONResponse(content={"data": data})