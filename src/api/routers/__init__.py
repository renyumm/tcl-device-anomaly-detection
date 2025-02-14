'''
LastEditors: renyumm strrenyumm@gmail.com
Date: 2024-10-17 13:44:16
LastEditTime: 2024-12-25 14:11:20
FilePath: /tcl-check-of-dirty-api/src/api/routers/__init__.py
'''
# routers/__init__.py
from .get_pie import router as get_pie_router
from .get_bar import router as get_bar_router
from .get_line import router as get_line_router
from .get_pareto import router as get_pareto_router
from .parse_data import router as parse_data_router

routers = [
    get_pie_router,
    get_bar_router,
    get_line_router,
    get_pareto_router,
    parse_data_router
]
