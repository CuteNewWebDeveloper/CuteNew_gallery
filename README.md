网页：https://cutenewwebdeveloper.github.io/CuteNew_gallery/  


---
<上传指南>  
将图片（jpg格式）命名为 ：`<时间> <地点> <作者名>.jpg`  
上传至仓库：`CuteNew_gallery/docs/input_material/`  
注意不是`CuteNew_gallery/docs/input_material/DonotDeleteME/`这是为了防止此路径被删除而设的  
workflow将自动更新图片详情页和总index页面  




---
<开发者笔记>**上传图片-自动处理生成静态网页工作流程：**  
-当CuteNew_gallery/docs/input_material/被更改时或手动，触发workflow（一个Python程序）；  
① 对每个CuteNew_gallery/docs/input_material/中的图片检测md5值，如果此md5已经与存在于CuteNew_gallery/docs/images/一个文件相同，跳过并删除此文件；  
② 不存在，则：  
②-① 原文件名split为三分：时间地点作者名，生成随机文件名。追加写入csv：图片id，图片名称，时间地点作者名等信息；  
②-② 复制到CuteNew_gallery/docs/images/；  
②-③ 复制到CuteNew_gallery/docs/images_preview/并转换为缩略图；  
②-④ 依据html模板生成图片展示页，并保存到CuteNew_gallery/docs/pages/；  
②-⑤ 按顺序，依据html模板更新gallery首页；  
②-⑥ 删除CuteNew_gallery/docs/input_material/中所有文件；  
③ github workflow推送所更改文件到仓库。  
