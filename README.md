# CuteNew Gallery

静态站点：[CuteNew Gallery](https://cutenewwebdeveloper.github.io/CuteNew_gallery/)

CuteNew Gallery 是 JetPhotos 航空摄影小组 CuteNew 的作品图库。图片来自公众号同步和经授权的组员投稿；如有版权问题，请联系小组删除。

## 上传一张图片

把 JPEG 放到 `docs/input_material/` 根目录，文件名必须是：

```text
<拍摄日期> <地点或机场代码> <摄影师姓名>.jpg
```

例如：

```text
2025.11.16 PEK Alice Zhang.jpg
```

推送到 `main` 后，**Ingest gallery uploads** Action 会：

1. 在不修改源上传文件的前提下校验文件名和图片内容；
2. 去重、生成右下角品牌水印与信息栏齐全的全尺寸图片，以及干净的 16:10 缩略图；
3. 更新 `image_log.csv`、页面、分页、日期/机场数据和浏览用 JSON；
4. 成功后才删除 `input_material` 里的已处理文件并提交生成结果。

格式错误的文件会保留在 `input_material`，Action 失败并给出原因，不会被静默删除。

## 架构

```text
docs/input_material/*.jpg
        │
        ▼
gallery/  (可测试的 Python 构建流水线)
        ├── docs/images/            全尺寸带版权栏图片 + image_log.csv
        ├── docs/images_preview/    16:10 缩略图
        ├── docs/pages/             单图详情页
        ├── docs/assets/            共享样式、交互脚本和品牌水印
        └── docs/*.html / *.csv / gallery-data.json
        │
        ▼
GitHub Pages
```

代码职责分开：

- `gallery/images.py`：图片归一化、自动品牌水印、版权信息栏和缩略图。
- `gallery/metadata.py`：CSV、校验、日期统计和去重清单。
- `gallery/render.py`：HTML、JSON、CSV 静态渲染。
- `gallery/pipeline.py`：入库及维护操作编排。
- `gallery/cli.py`：本地与 GitHub Actions 的统一命令行入口。

保留了 `auto_update.py`、`update_bar.py`、`crop_images.py` 作为旧命令兼容壳；新代码应优先使用 `python -m gallery …`。

`docs/assets/site.css` 和 `docs/assets/site.js` 由 `python -m gallery rebuild` 从 `gallery/render.py` 生成；修改站点视觉或按钮交互时请改渲染源，不要直接改生成文件。`docs/assets/brand-watermark.png` 同时用于页眉与新上传全尺寸图片的自动品牌水印。

## GitHub Actions

| 工作流 | 触发方式 | 用途 |
| --- | --- | --- |
| `Ingest gallery uploads` | 上传到 `docs/input_material/` 或手动运行 | 正常入库和重建站点 |
| `Test gallery pipeline` | Pull Request、核心代码变更 | 执行隔离测试 |
| `Refresh gallery watermark bars` | 手动运行 | 从 `image_log.csv` 重做所有全图底栏 |
| `Crop existing preview images` | 手动运行 | 批量裁剪历史缩略图为 16:10 |

后三项会修改大量二进制文件，因此刻意不在普通上传时自动执行。所有写入型工作流都声明了最小的 `contents: write` 权限和并发锁，避免并发 push 互相覆盖。

## 本地开发

需要 Python 3.11+：

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v

# 处理待上传图片
python -m gallery ingest

# 只从现有 image_log.csv 重建页面/数据
python -m gallery rebuild

# 显式维护任务（会改写大量图片）
python -m gallery watermark
python -m gallery crop-previews
```

首次在完整仓库副本中运行入库命令时会建立 `docs/images/image_manifest.json`，以后可用于快速可靠地识别已有全图。仓库目前仍直接跟踪原始图片；迁移到 Git LFS 或对象存储是独立的数据迁移项目，不应与日常代码重构混在同一个提交里。
