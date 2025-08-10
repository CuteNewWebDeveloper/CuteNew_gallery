网页：https://cutenewwebdeveloper.github.io/CuteNew_gallery/  

---
## 🚀 **CuteNew Gallery 简介 | About CuteNew Gallery** ✈️

**🇨🇳 中文说明：**  
**CuteNew Gallery** 是 [JetPhotos 航空摄影小组（Spotting Group）CuteNew](https://www.jetphotos.com/group/309) 的 **小型高质量航空摄影图库**，为组员提供一个 **额外发布优秀作品** 的平台。  

本站图片主要来自 **两个渠道**：  
1️⃣ **公众号同步** —— 微信公众号 **「Cute New 航空摄影」** 已发布和将发布的文章图片会同步到本站。  
2️⃣ **组员投稿** —— 小组成员可单独投稿高质量图片。  

因此，有些图片可能会同时带有 **JetPhotos、Airplane-Pictures** 或 **个人水印** —— **我们已获得作者授权**。  

📌 **版权声明**：如果您认为本站图片侵犯了版权，并且看到了这段声明，请**立即联系我们**删除相关内容。  

---

**🇬🇧 English Notice:**  
**CuteNew Gallery** is a **small-scale high-quality aviation photography gallery** for members of the [JetPhotos Spotting Group CuteNew](https://www.jetphotos.com/group/309).  
It serves as an **additional platform** for members to showcase excellent works.  

Images on this site mainly come from **two sources**:  
1️⃣ **WeChat Synchronization** — All images published (past & future) on our official WeChat account **“Cute New Aviation Photography”** are synchronized here.  
2️⃣ **Member Submissions** — High-quality images submitted directly by group members.  

Some images may carry **JetPhotos, Airplane-Pictures, or personal watermarks** — **we have obtained the authors’ permission**.  

📌 **Copyright Notice**: If you believe any image here infringes your rights and you have read this notice, please **contact us immediately** for removal.

---
<上传指南>  
将图片（jpg格式）命名为 ：`<时间> <地点> <作者名>.jpg`  
上传至仓库：`CuteNew_gallery/docs/input_material/`  
注意不是`CuteNew_gallery/docs/input_material/DonotDeleteME/`这是为了防止此路径被删除而设的  
workflow将自动更新图片详情页和首页  




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
