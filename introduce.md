# 介绍

网格参数化算法就是将计算机中的三维网格曲面“展平”到二维平面上，生活中常见的“展平”的案例包括：地球仪的展平与汽车贴膜等，在游戏工业中将原始曲面展到平面上，美术再对展平的图形贴上色彩纹理或者是细微凹凸的高频信息这个过程称之为纹理映射(Texture Mapping)

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/application.png" alt="application" style="zoom: 67%;" />

由于在计算机中渲染管线最终是对三角形进行渲染，所以上面“展平”的过程也就是求解这样的一个映射

$f :M \mapsto M'$,将嵌入在$R^3$中的三角网格M映射到嵌入在$R^2$中的三角网格M'

![param_intro](https://lgximgs.oss-cn-beijing.aliyuncs.com/param_intro.png)
<center>
左图是$R^3$中的三角网格M，右图是$R^2$中的三角网格M'
</center>
这个映射在大多数情况下是非平凡的(Non-Trivial)（在某些2.5D的场景下可以是平凡的，只要将z值设为0即可），具体来说需要满足以下的一些约束，
映射是双射的，三角形不能翻转（flip over free）,三角形边不能自相交（self-intersection free）
并且希望映射所造成的图像扭曲变形能尽可能小
