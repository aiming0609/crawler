# 4K高清壁纸下载器

一个功能强大的壁纸下载工具，支持分类下载、关键词搜索和智能过滤，专注于下载高质量的电脑壁纸。

## 功能特性

1. **多种下载模式**
   - 按分类下载：支持动漫、风景、游戏等多个分类
   - 关键词搜索：支持搜索特定主题的壁纸
   - 分类内搜索：可在指定分类中搜索关键词

2. **智能过滤**
   - 自动过滤低分辨率图片（最低1920x1080）
   - 自动过滤竖屏图片（手机壁纸）
   - 智能判断图片尺寸和类型

3. **下载优化**
   - 自动处理重复下载
   - 智能文件命名，移除无用信息
   - 支持中断后继续下载
   - 自动获取总页数，智能调整下载页数

4. **稳定性保障**
   - 随机延时，避免请求过快
   - 自动处理网络异常
   - 优雅的程序退出机制
   - 自动清理资源

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. **按分类下载**
```python
crawler = WallpaperCrawler()
crawler.start(category='4kdongman', pages=3)  # 下载动漫分类的前3页
```

2. **按关键词搜索**
```python
crawler.start(keyword='原神', pages=2)  # 搜索"原神"相关壁纸
```

3. **在分类中搜索**
```python
crawler.start(category='4kdongman', keyword='原神', pages=2)  # 在动漫分类中搜索
```

## 可用分类

- `4kdongman`: 动漫壁纸
- `4kfengjing`: 风景壁纸
- `4kyouxi`: 游戏壁纸
- `4kyingshi`: 影视壁纸
- `4kqiche`: 汽车壁纸
- `4kdongwu`: 动物壁纸
- `4krenwu`: 人物壁纸
- `4kmeizi`: 美女壁纸
- `4kmeinv`: 美女壁纸
- `4kzongjiao`: 宗教壁纸

## 项目依赖

- Python 3.6+
- requests：网络请求
- beautifulsoup4：HTML解析
- selenium：网页自动化
- undetected-chromedriver：反爬虫
- fake-useragent：随机User-Agent

## 注意事项

1. 需要安装Chrome浏览器
2. 程序会自动检测Chrome版本
3. 下载的壁纸保存在 `wallpapers` 目录
4. 支持按Ctrl+C随时中断下载
5. 默认只下载横屏且分辨率≥1920x1080的图片

## 文件说明

- `wallpaper_crawler.py`: 主程序文件
- `requirements.txt`: 依赖列表
- `wallpapers/`: 下载的壁纸保存目录

## 更新日志

### v1.0.0
- 实现基本的壁纸下载功能
- 支持分类和搜索
- 添加分辨率过滤
- 优化文件命名
- 添加断点续传支持

## 待优化
- [ ] 添加多线程下载支持
- [ ] 优化内存使用
- [ ] 添加下载进度条
- [ ] 支持自定义下载目录
- [ ] 添加命令行参数支持