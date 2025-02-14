# pipreqs . --force
###
 # @LastEditors: renyumm strrenyumm@gmail.com
 # @Date: 2024-12-26 09:32:08
 # @LastEditTime: 2025-02-11 16:38:36
 # @FilePath: /tcl-check-of-dirty-api/build.sh
### 
factory=${1:-dw5}
echo $factory
docker build -t tcl-check-of-dirty:${factory} --build-arg FACTORY=${factory}  .
docker tag tcl-check-of-dirty:${factory} witpark-hzregistry.tjsemi.com/zhai/tcl-check-of-dirty:${factory}
docker push witpark-hzregistry.tjsemi.com/zhai/tcl-check-of-dirty:${factory}