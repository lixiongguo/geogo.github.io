## 工程环境搭建

## 前端工程

前端工程在超融合上登录31号服务器拷贝过来

![image-20260119185351489](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260119185351489.png)

采用已给的node.js

![image-20260119185634421](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260119185634421.png)

不用自己下载依赖包，采用自带的

![image-20260119185709403](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260119185709403.png)

## 后端工程

微服务，所以只要启二开的工程就可以

![image-20260119185816789](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260119185816789.png)

什么样报错添加

### 后端如有报错，注意hosts添加域名

![image-20260119185736493](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260119185736493.png)

## 开发调试流程

1.前端增加页面，前端开发页面(注意路由的配置)

![image-20260120164845880](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120164845880.png)

只有测试服的sysadmin_AM是@，其余都是!(注意中英文)

2.后端开发功能，Postman调试后端接口

3.通过提供的监控工具，在22服上暂时关停测试服环境

![image-20260120094316553](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120094316553.png)

4.后端mvn package打包并替换

下面这个编码的报错没什么问题

![image-20260120090248383](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120090248383.png)



5.前端npm build 打包，将dist文件夹放到nginx目录下

使用这个build.bat打包

![image-20260120111755742](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120111755742.png)

![image-20260120112050239](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120112050239.png)

将dist文件夹放到22的nginx目录下，重命名替换掉html文件夹

![image-20260120112904170](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120112904170.png)

# postman测试接口

![image-20260119184835727](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260119184835727.png)

token拷贝过来

![image-20260119184955533](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260119184955533.png)

后端接口定义

![image-20260119184915147](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260119184915147.png)

target下存放生成的新包

![image-20260120094213816](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120094213816.png)

测试服23下

![image-20260120094140239](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120094140239.png)

然后再22服上重启

Swagger测试接口

![image-20260120102401859](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120102401859.png)

注意看nacos下是否是只有现在的服务

![image-20260120102303853](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120102303853.png)![image-20260120102303924](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120102303924.png)

代理规则在vue.config.js

![image-20260120111952541](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120111952541.png)

注意域名定在hosts文件中定义的

本地服避免在Nacos上与测试环境服冲突，在application.yml和boostrap.yml都要改一下

![image-20260120141853779](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120141853779.png)

![image-20260120142000356](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120142000356.png)

避免集群选择错误的服务

![image-20260120142331963](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120142331963.png)



nacos密码

![image-20260120160737164](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120160737164.png)

通过网盘传输文件

![image-20260120161739803](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120161739803.png)

![image-20260120162905413](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120162905413.png)

正式服(31)前端部署地址

![image-20260120164409526](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120164409526.png)

![image-20260120171752659](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260120171752659.png)

postman调试

![image-20260126154555276](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260126154555276.png)

![image-20260126154820265](C:\Users\lixio\AppData\Roaming\Typora\typora-user-images\image-20260126154820265.png)