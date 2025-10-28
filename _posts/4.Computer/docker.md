pycharm中

切换工程的python版本

![image-20250619164754401](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250619164754401.png)

直接将之前python版本的包复制过来就可以

docker的安装

https://blog.csdn.net/weixin_71699295/article/details/137387383

### 1.在本地（127.0.0.1）,不带IO设备(相机,光谱仪等)

dockerfile

![image-20250618162906577](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618162906577.png)

COPY .. 拷贝所有项目文件

基础镜像python 3.8-slim轻量化

![image-20250618163151371](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618163151371.png)

**docker build -t flask-app .** 

按照dockerfile中构建docker镜像

![image-20250618162830221](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618162830221.png)

**docker run -p 5001:5001 flask-app** 

端口映射

![image-20250618162554521](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618162554521.png)

![image-20250618162738574](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618162738574.png)

docker desktop需要启动作为守护进程

![image-20250618162127996](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618162127996.png)

需要配置国内镜像否则下载不到基础镜像

![image-20250618163000634](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618163000634.png)

![image-20250618163031029](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618163031029.png)

![image-20250618161947394](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618161947394.png)

![image-20250618163117696](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618163117696.png)

![image-20250618164053094](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618164053094.png)

flask监听

![image-20250618161607522](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618161607522.png)

![image-20250618161641694](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618161641694.png)

要禁用缓存否则print的时候没有调试输出，（也可以在print的后面加上flush=true）

![image-20250618162213381](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618162213381.png)



![image-20250618164545682](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618164545682.png)

![image-20250618164432540](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618164432540.png)

![image-20250618164715532](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618164715532.png)

![image-20250618165128593](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618165128593.png)

![image-20250618164728000](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618164728000.png)



![image-20250618165032339](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618165032339.png)



![image-20250618172322269](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618172322269.png)

**修改到D盘后，之前的镜像资源会自动迁移过去**

## 2.另外一台机器上作为后端,不带IO设备

1.1在另外一台机器上docker镜像跑起来

docker save保存镜像

![image-20250618165714534](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618165714534.png)

![image-20250618170321120](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618170321120.png)

![image-20250618170236822](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618170236822.png)

镜像比工程文件夹整体都大，多出来的是基础镜像？

docker load -i **.tar来加载



![image-20250618171906794](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250618171906794.png)

2.如何访问

WSL的虚拟IP地址

![image-20250619150544622](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250619150544622.png)

![image-20250619150633334](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250619150633334.png)

**可以通过宿主机的IP地址访问Docker**

**3.尝试带相机**

opencv-python缺少linux版的库

libGL.so

![image-20250619155807538](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250619155807538.png)

同理libgthread.so

![image-20250619155935404](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250619155935404.png)

![image-20250619155833801](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250619155833801.png)

**难题：镜像是基于Linux系统的所以用的是Linux的库（*.so）,而我们的开发都是基于Windows的**

下载windows镜像的问题，一定要企业版？

![image-20250619171501599](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250619171501599.png)