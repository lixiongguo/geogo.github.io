![image-20251015101857395](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015101857395.png)

![image-20250205111544090](C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20250205111544090.png)

无论是网格的几何变形以及参数化都是对某种能量求最优化

其中一个主要的问题就是几何能量的优化的耗时较长

![image-20250205111952838](C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20250205111952838.png)

二阶方法会随着问题的规模迅速变得intractable

![image-20250205112157344](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205112157344.png)

![image-20250205113001895](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205113001895.png)

innovation来自两个重要的观察

![image-20250205113126959](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205113126959.png)

两个观察相互间是互相印证的

![image-20250205113333728](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205113333728.png)

事实上就是对如下的能量进行求优化

![image-20250205113532455](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205113532455.png)

proximal方法

![image-20250205135747088](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205135747088.png)

将f分解为g和h，h是严格凸的
![image-20250205113710419](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205113710419.png)

具体的能量分解

![image-20250205113837393](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205113837393.png)

这个方法本质上也是个一阶方法

![image-20250205113938063](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205113938063.png)

使用Newton方法依赖于求解下面的线性KKT条件

![image-20250205114624709](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205114624709.png)

![image-20250205174212265](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205174212265.png)

![image-20250205174325449](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205174325449.png)

![image-20250205175201355](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205175201355.png)

![image-20250205134809087](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205134809087.png)

![image-20250205134731846](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205134731846.png)

![image-20250205134913364](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205134913364.png)

![image-20250205175023492](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250205175023492.png)

![image-20250207112617561](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250207112617561.png)