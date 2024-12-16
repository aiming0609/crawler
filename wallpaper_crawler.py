import os
import time
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin, quote
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import subprocess
import signal
import sys

def encode_keyword(keyword):
    """特殊编码搜索关键词"""
    # 将中文转换为GBK编码的字节，然后转为十六进制
    encoded = ''
    for char in keyword.encode('gbk'):
        encoded += '%' + hex(char)[2:].upper()
    return encoded

class WallpaperCrawler:
    def __init__(self):
        self.base_url = 'https://pic.netbian.com'
        self.download_dir = 'wallpapers'
        self.ua = UserAgent()
        self.ensure_download_dir()
        self.driver = None
        self.wait = None
        self.max_duplicates = 5  # 最大重复次数
        self.duplicate_count = 0  # 重复计数器
        self.chrome_version = self.get_chrome_version()
        
        # 注册信号处理函���
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """处理程序退出信号"""
        print('\n正在清理资源...')
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """清理资源"""
        if self.driver:
            try:
                # 直接关闭所有相关进程
                self.driver.service.process.kill()
            except:
                pass
            self.driver = None

    def get_chrome_version(self):
        """获取Chrome浏览器版本"""
        try:
            # Windows系统
            cmd = 'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
            output = subprocess.check_output(cmd, shell=True).decode()
            version = output.strip().split()[-1]
            print(f'检测到Chrome版本: {version}')
            return int(version.split('.')[0])  # 只返回主版本号
        except:
            print('无法从注册表获取Chrome版本，使用默认版本120')
            return 120  # 使用较新的版本号

    def setup_driver(self):
        """设置Chrome浏览器"""
        self.cleanup()  # 先清理现有的driver
        
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')  # 新版无界面模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={self.ua.random}')
        
        try:
            # 创建浏览器实例，指定Chrome版本
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=None,  # 自动下载
                browser_executable_path=None,  # 自动查找
                suppress_welcome=True,  # 禁用欢迎页
                version_main=self.chrome_version,  # 指定Chrome版本
                headless=True  # 确保无界面模式
            )
            
            # 设置等待时间
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 10)
            
            # 访问首页以初始化会话
            self.driver.get(self.base_url)
            time.sleep(random.uniform(2, 3))
            
        except Exception as e:
            print(f'浏览器初始化失败: {e}')
            self.cleanup()
            raise

    def ensure_download_dir(self):
        """确保下载目录存在"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def sanitize_filename(self, filename):
        """清理文件名，移除非法字符和不必要的信息"""
        # 移除HTML标签
        filename = re.sub(r'<[^>]+>', '', filename)
        
        # 移除常见的后缀词
        remove_words = [
            '4K壁纸', '4k壁纸', '高清壁纸', '电脑壁纸', '超清壁纸', 
            '4K', '4k', '壁纸', '图片', 'font', '_font',
            '3840x2160', '3840x2400', '2560x1600', '2400x1080',
            '高清', '超清', '电脑', 'color', 'red'
        ]
        
        # 替换Windows文件名中的非法字符
        filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
        
        # 移除不必要的信息
        for word in remove_words:
            filename = filename.replace(word, '')
        
        # 移除连续的下划线、空格和引号
        filename = re.sub(r'[_\s\'\"]+', '_', filename)
        
        # 移除前后的下划线、空格和引号
        filename = filename.strip('_').strip().strip('\'\"')
        
        return filename

    def get_wallpapers(self, category=None, page=1, keyword=None):
        """获取壁纸列表"""
        try:
            # 检查keyword是否为有效的搜索词
            if keyword and keyword.strip():  # 只有��keyword不为空且不全是空白字符时才进行搜索
                # 搜索模式的代码...
                if page == 1:
                    # 访问搜索页面
                    search_url = f'{self.base_url}/e/search/index.php'
                    self.driver.get(search_url)
                    time.sleep(2)
                    
                    try:
                        # 等待搜索框加载
                        search_input = self.wait.until(
                            EC.presence_of_element_located((By.NAME, 'keyboard'))
                        )
                        
                        # 清空搜索框并输入关键词
                        search_input.clear()
                        search_input.send_keys(keyword)
                        
                        # 如果有分类，选择分类
                        if category:
                            try:
                                classid_input = self.driver.find_element(By.NAME, 'classid')
                                classid_input.clear()
                                classid_input.send_keys(category)
                            except:
                                print('未找到分类输入框')
                        
                        # 提交搜索表单
                        search_input.submit()
                        time.sleep(3)  # 等待搜索结果加载
                        
                    except Exception as e:
                        print(f'搜索操作失败: {e}')
                        return []
                    
                    # 获取搜索结果页面的URL
                    current_url = self.driver.current_url
                    print(f'搜索结果页面: {current_url}')
                    
                    # 检查是否有结果页面
                    if 'result' not in current_url and 'search' not in current_url:
                        print('搜索失败，未能获取结果页面')
                        return []
                    
                    # 存储搜索ID，用于翻页
                    try:
                        if 'searchid=' in current_url:
                            self.search_id = current_url.split('searchid=')[-1].split('&')[0]
                            print(f'获取搜索ID: {self.search_id}')
                    except:
                        print('无法获取搜索ID，可能影响翻页')
                    
                else:
                    # 翻页
                    if hasattr(self, 'search_id'):
                        url = f'{self.base_url}/e/search/result/index.php?page={page}&searchid={self.search_id}'
                        if category:
                            url += f'&classid={category}'
                    else:
                        # 如果没有搜索ID，尝试直接访问搜索页面
                        url = f'{self.base_url}/e/search/result/?keyboard={encode_keyword(keyword)}&page={page}'
                        if category:
                            url += f'&classid={category}'
                    
                    print(f'访问翻页: {url}')
                    self.driver.get(url)
                    time.sleep(2)
            else:
                # 纯分类模式
                if page == 1:
                    url = f'{self.base_url}/{category}/'
                else:
                    url = f'{self.base_url}/{category}/index_{page}.html'
                print(f'访问页面: {url}')
                self.driver.get(url)
                time.sleep(2)
            
            # 等待图片列表加载
            try:
                # 尝试多个可能的选择器
                selectors = [
                    '.slist ul li',  # 搜索结果
                    '#main .slist ul li',  # 分类页面
                    '.slist li',  # 备选
                    '.slist .clearfix li'  # 备选
                ]
                
                for selector in selectors:
                    try:
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        items_selector = selector
                        break
                    except:
                        continue
                else:
                    print('未找到图片列表，可能是页结构变化')
                    return []
                
            except Exception as e:
                print(f'等待图片列表加载失败: {e}')
                return []
            
            # 获取页面内容
            content = self.driver.page_source
            soup = BeautifulSoup(content, 'html.parser')
            
            # 解析图片列表
            items = []
            for item in soup.select(items_selector):
                try:
                    link = item.find('a')
                    img = item.find('img')
                    if link and img:
                        # 清理标题中的HTML标签
                        title = img.get('alt', '').strip()
                        title = re.sub(r'<[^>]+>', '', title)
                        items.append({
                            'url': urljoin(self.base_url, link['href']),
                            'title': title,
                            'thumb': urljoin(self.base_url, img['src'])
                        })
                except Exception as e:
                    print(f'解析列表项出错: {e}')
                    continue
            
            if not items:
                print('未找到任何图片')
            else:
                print(f'找到 {len(items)} 张图片')
                # 打印前几个结果的题
                for i, item in enumerate(items[:3]):
                    print(f'- {item["title"]}')
            
            return items
            
        except Exception as e:
            print(f'获取壁纸列表出错: {e}')
            return []

    def is_desktop_wallpaper(self, img_element):
        """判断是否为电脑壁纸（横屏）且分辨率至少为1920x1080"""
        try:
            # 获取图片原始尺寸
            width = img_element.get_attribute('naturalWidth')
            height = img_element.get_attribute('naturalHeight')
            
            if width and height:
                width = int(width)
                height = int(height)
                # 检查是否为横屏且分辨率至少为1920x1080
                if width > height and width >= 1920 and height >= 1080:
                    print(f'符合要求的壁纸: {width}x{height}')
                    return True
                else:
                    if width <= height:
                        print(f'跳过竖屏图片: {width}x{height}')
                    else:
                        print(f'跳过低分辨率图片: {width}x{height}')
                    return False
            
            # 如果无法获取尺寸，尝试从标题中判断
            title = img_element.get_attribute('alt') or ''
            # 只匹配高分辨率的横屏尺寸
            desktop_resolutions = [
                '3840x2160', '2560x1440', '2560x1600',
                '3440x1440', '2880x1800', '1920x1080',
                '1920x1200', '2560x1080'
            ]
            for res in desktop_resolutions:
                if res in title:
                    print(f'从标题判断为高清电脑壁纸: {res}')
                    return True
            
            # 如果无法判断分辨率，则不下载
            print('无法确定分辨率，跳过下载')
            return False
            
        except Exception as e:
            print(f'判断壁纸类型出错: {e}')
            return False  # 出错时不下载

    def download_wallpaper(self, photo):
        """下载单张壁纸"""
        try:
            # 随机延时
            time.sleep(random.uniform(2, 3))
            
            # 访问详情页
            self.driver.get(photo['url'])
            
            # 等待图片加载
            img_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#img img')))
            
            # 检查是否为电脑壁纸
            if not self.is_desktop_wallpaper(img_element):
                return False
            
            # 获取图片URL
            img_url = img_element.get_attribute('src')
            if not img_url:
                print(f'未找到图片链接: {photo["url"]}')
                return False
            
            if not img_url.startswith('http'):
                img_url = urljoin(self.base_url, img_url)
            
            # 生成文件名
            title = self.sanitize_filename(photo['title'])
            timestamp = img_url.split('/')[-1].split('.')[0]  # 提取时间戳
            ext = img_url.split('.')[-1]  # 提取扩展名
            
            # 如果标题为空或只包含特殊字符，使用时间戳作为文件名
            if not title or not re.search(r'[a-zA-Z0-9\u4e00-\u9fff]', title):
                filename = f"{timestamp}.{ext}"
            else:
                filename = f"{title}_{timestamp[-6:]}.{ext}"  # 只使用时间戳的后6位
            
            filepath = os.path.join(self.download_dir, filename)

            # 如果文件已存在，跳过下载
            if os.path.exists(filepath):
                print(f'文件已存在: {filename}')
                self.duplicate_count += 1  # 增加重复计数
                return False

            # 获取Cookie
            cookies = self.driver.get_cookies()
            cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
            
            # 构建headers
            headers = {
                'User-Agent': self.driver.execute_script('return navigator.userAgent'),
                'Referer': photo['url'],
                'Cookie': cookie_str,
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
            # 下载图片
            response = requests.get(img_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f'成功下载: {filename}')
            self.duplicate_count = 0  # 重置重复计数
            return True

        except Exception as e:
            print(f'下载壁纸出错: {e}')
            return False

    def get_total_pages(self, content):
        """从页面内容中获取总页数"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找分页信息
            page_div = soup.find('div', class_='page')
            if not page_div:
                # 如果没有分页div，检查是否有内容
                if soup.select('.slist ul li'):
                    return 1
                return 0
            
            # 获取所有页码链接
            page_links = page_div.find_all('a')
            if not page_links:
                if soup.select('.slist ul li'):
                    return 1
                return 0
            
            max_page = 1
            for link in page_links:
                # 尝试链接中提取页码
                href = link.get('href', '')
                if 'index_' in href:
                    try:
                        page_num = int(href.split('index_')[-1].split('.')[0])
                        max_page = max(max_page, page_num)
                    except:
                        continue
                elif link.text.isdigit():
                    try:
                        page_num = int(link.text)
                        max_page = max(max_page, page_num)
                    except:
                        continue
            
            return max_page if max_page > 0 else 1
            
        except Exception as e:
            print(f'获取总页数出错: {e}')
            return 1  # 出错时返回1，确保至少下载第一页

    def start(self, category=None, keyword=None, pages=3):
        """开始爬取壁纸
        
        参数:
            category: 分类名称，如 '4kdongman'
            keyword: 搜索关键词
            pages: 要下载的页数
        """
        try:
            # 检查参数有效性
            if not category and (not keyword or not keyword.strip()):
                print('请至少指定有效的分类或关键词之一')
                return
                
            if keyword and keyword.strip():
                if category:
                    print(f'开始在分类 [{category}] 中搜索并下载壁纸，关键词: {keyword}，页数: {pages}')
                else:
                    print(f'开始搜索并下载壁纸，关键词: {keyword}，页数: {pages}')
            else:
                print(f'开始下载壁纸，分类: {category}，页数: {pages}')
            
            # 先获取第一页内容以确定总页数
            self.setup_driver()
            wallpapers = self.get_wallpapers(category, 1, keyword)
            
            if not wallpapers:
                print('未找到任何壁纸')
                self.cleanup()
                return
            
            # 获取总页数
            total_pages = self.get_total_pages(self.driver.page_source)
            if total_pages == 0:
                print('无法获取总页数')
                self.cleanup()
                return
            
            # 确定实际要下载的页数
            actual_pages = min(pages, total_pages)
            print(f'总页数: {total_pages}，将下载: {actual_pages} 页')
            
            # 下载第一页
            for photo in wallpapers:
                if self.duplicate_count >= self.max_duplicates:
                    print(f'重复次数过多（{self.duplicate_count}次），跳过当前页面')
                    break
                self.download_wallpaper(photo)
                time.sleep(random.uniform(2, 3))
            
            # 清理第一页的浏览器
            self.cleanup()
            
            # 下载剩余页面
            for page in range(2, actual_pages + 1):
                print(f'\n正在处理第 {page}/{actual_pages} 页')
                
                # 每页都重新初始化浏览器
                self.setup_driver()
                
                wallpapers = self.get_wallpapers(category, page, keyword)
                
                if not wallpapers:
                    print(f'第 {page} 页没有找到壁纸，尝试下一页')
                    self.cleanup()
                    continue
                
                # 重置重复计数
                self.duplicate_count = 0
                    
                for photo in wallpapers:
                    # 检查重复次数是否超过限制
                    if self.duplicate_count >= self.max_duplicates:
                        print(f'重复次数过多（{self.duplicate_count}次），跳过当前页面')
                        break
                        
                    self.download_wallpaper(photo)
                    # 添加随机延时，避免请求过于频繁
                    time.sleep(random.uniform(2, 3))
                
                # 清理当前页的浏览器
                self.cleanup()
                    
        except Exception as e:
            print(f'爬虫运行出错: {e}')
        finally:
            # 确保清理资源
            self.cleanup()

if __name__ == '__main__':
    try:
        crawler = WallpaperCrawler()
        
        # 使用示例：
        # 1. 下载动漫分类的第1页
        crawler.start(category='4kdongman', pages=1)
        
        # 2. 搜索原神壁纸
        # crawler.start(keyword='原神', pages=2)
        
        # 3. 在动漫分类中搜索原神
        # crawler.start(category='4kdongman', keyword='原神', pages=2)
        
        # 4. 下载风景分类的前3页
        # crawler.start(category='4kfengjing', pages=3)
        
        # 5. 在游戏分类中搜索英雄联盟
        # crawler.start(category='4kyouxi', keyword='英雄联盟', pages=2)
        
    except KeyboardInterrupt:
        print('\n程序被用户中断')
    except Exception as e:
        print(f'程序出错: {e}')
    finally:
        # 确保程序正常退出
        sys.exit(0)
    
    # 分类参考：
    # - 4kmeizi: 美女
    # - 4kfengjing: 风景
    # - 4kdongman: 动漫
    # - 4kyouxi: 游戏
    # - 4kmeinv: 美女
    # - 4kyingshi: 影视
    # - 4kqiche: 汽车
    # - 4kdongwu: 动物
    # - 4krenwu: 人物
    # - 4kzongjiao: 宗教