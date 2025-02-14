<!--
 * @LastEditors: renyumm strrenyumm@gmail.com
 * @Date: 2025-02-10 15:32:45
 * @LastEditTime: 2025-02-10 15:56:05
 * @FilePath: /tcl-check-of-dirty-api/aaa.md
-->
project_root/
├── config/
│   ├── default.yaml           # 默认配置，最基础的配置
│   ├── products/             # 按产品类型的配置
│   │   ├── coolant.yaml
│   │   ├── sheave.yaml
│   │   └── steelwire.yaml
│   └── factories/            # 按工厂的配置
│       ├── dw1/
│       │   ├── config.yaml   # 工厂级别配置
│       │   ├── coolant.yaml
│       │   ├── sheave.yaml
│       │   └── steelwire.yaml
│       ├── dw2/
│       ├── dw3/
│       └── dw4/
├── src/
└── main.py