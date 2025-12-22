import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
import datetime

time = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))

LABEL = [
    "快訊",
    "直擊",
    "獨家",
    "天氣",
    "民調",
    "專訪",
    "影",
    "獨",
    "ATP年終賽",
    "LTN經濟通》",
    
]


# 抓新聞連結
class CatchNews:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/"
        })  


    def _get_soup(self, url):
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError as e:
            print(f"[ERROR] {url} HTTPError:", e)
            return None
        except requests.RequestException as e:
            print(f"[ERROR] {url} RequestException:", e)
            return None

        return BeautifulSoup(resp.text, "html5lib")

    # 中國時報爬蟲 
    def chinatimes(self):       
        links = []
        base = "https://www.chinatimes.com"
        url = base + "/realtimenews/?chdtv"

        soup = self._get_soup(url)
    
        news_list = soup.find_all("div", class_="cropper")

        for news in news_list:
            href = news.find("a").get("href")
            links.append(urljoin(base, href))
        
        return links

    # ETtoday爬蟲
    def ettoday(self):      
        links = []

        base = "https://www.ettoday.net"
        url = base + "/news/hot-news.htm"

        soup = self._get_soup(url)

        news_list = soup.select("div.part_pictxt_3 div.piece.clearfix h3 > a")

        for news in news_list:
            href = news.get("href")
            links.append(urljoin(base, href))
            
        return links
    
    # LTN爬蟲
    def ltn(self):
        links = []
        
        base = "https://news.ltn.com.tw"
        url = base + "/list/breakingnews/popular"

        soup = self._get_soup(url)

        news_list = soup.find_all("ul", class_="list")

        for news in news_list:
            for li in news.find_all("li"):
                a = li.find("a", href=True)
                if not a:              # 防呆：沒有 <a> 就跳過
                    continue
                href = a.get("href")
                if not href:
                    continue
                links.append(urljoin(base, href))

        return links
    
    # SETN 爬蟲
    def setn(self):
        links = []

        base = "https://www.setn.com"
        url = "https://www.setn.com/ViewAll.aspx?PageGroupID=0"

        soup = self._get_soup(url)

        news_list = soup.find_all("div", class_="col-sm-12 newsItems")

        for news in news_list:
            a = news.find("a", class_="gt", href=True)
            
            links.append(urljoin(base, a["href"]))

        return links
    
    # TVBS 爬蟲
    def tvbs(self):
        links = []

        base = "https://news.tvbs.com.tw"
        url = base + "/hot"

        soup = self._get_soup(url)

        news_list = soup.find_all("div", class_="list")

        for news in news_list:
            for li in news.find_all("li"):
                a = li.find("a", href=True)
                if not a:              # 防呆：沒有 <a> 就跳過
                    continue
                href = a.get("href")
                if not href:
                    continue
                if re.search(r"^/[a-z\-]+/\d+$", href):
                    links.append(urljoin(base, href))

        return links
    
    # udn 爬蟲
    def udn(self):
        links = []

        base = "https://udn.com"
        url = base + "/rank/pv/2"

        soup = self._get_soup(url)

        news_list = soup.find_all("div", class_="story-list__text")

        for news in news_list:
            a = news.find("a", href=True)
            if not a:
                continue

            href = a.get("href")
            if not href:
                continue

            if href == "#" or href.startswith("#"):
                continue
            links.append(urljoin(base, href))
            
        # TODO: 刷新頁面造成無法擷取後半部分

        return links
    
    # yahoo 爬蟲
    def yahoo(self):
        url = "https://tw.news.yahoo.com/_td-news/api/resource?bkt=t5-twnews-bts-p13n%2Ct1-pc-twnews-article-rr-onegam&crumb=r4MhVhc7wAX&device=desktop&ecma=modern&feature=oathPlayer%2CenableEvPlayer%2CenableGAMAds%2CenableGAMEdgeToEdge%2CvideoDocking%2CenableRightRailGAMAds&intl=tw&lang=zh-Hant-TW&partner=none&prid=65c4dn1kidvs2&region=TW&site=news&tz=Asia%2FTaipei&ver=2.3.3197"
        
        req_payload = {
            "requests":{
                "g0":{
                    "resource":"ApacStreamService",
                    "operation":"read",
                    "params":{
                        "ncpParams":{
                            "body":{
                                "gqlVariables":{
                                    "main":{
                                        "pagination":{
                                            "nextParams":{
                                                "count":170,
                                                "snippetCount":20,
                                                "paginationUuids":""}
                                        }
                                    }
                                }
                            }
                        },
                        "useNCP":True,
                        "useCG":True,
                    }
                }
            },
            "context":{
                "feature":"oathPlayer,enableEvPlayer,enableGAMAds,enableGAMEdgeToEdge,videoDocking,enableRightRailGAMAds",
                "bkt":[
                    "t5-twnews-bts-p13n",
                    "t1-pc-twnews-article-rr-onegam"
                ],
                "crumb":"r4MhVhc7wAX",
                "device":"desktop",
                "intl":"tw",
                "lang":"zh-Hant-TW",
                "partner":"none",
                "prid":"1vnqestkiid1k", # 會變動的數值
                "region":"TW",
                "site":"news",
                "tz":"Asia/Taipei",
                "ver":"2.3.3197",
                "ecma":"modern"
            }
        }

        resp = requests.post(url, headers=self.session.headers ,json=req_payload, timeout=10)
        data = resp.json()["g0"]["data"]["stream_pagination"]["gqlVariables"]["main"]["pagination"]["nextParams"]["paginationUuids"]

        data = json.dumps(data, ensure_ascii=False, indent=2)

        # 找新聞payload
        payload = {
            "requests":{
                "g0":{
                    "resource":"ApacStreamService",
                    "operation":"read","params":{
                        "ui":{
                            "comments":True,
                            "editorial_featured_count":1,
                            "image_quality_override":True,
                            "link_out_allowed":True,
                            "ntk_bypassA3c":True,
                            "pubtime_maxage":0,
                            "relative_links":True,
                            "show_comment_count":True,
                            "smart_crop":True,
                            "storyline_count":2,
                            "storyline_min":2,
                            "summary":True,
                            "thumbnail_size":100,
                            "view":"mega",
                            "editorial_content_count":0,
                            "finance_upsell_threshold":4
                        },
                        "forceJpg":True,
                        "releasesParams":{
                            "limit":159,
                            "offset":0
                        },
                        "ncpParams":{
                            "query":{
                                "adsSlotsEnabled":True,
                                "namespace":"abu",
                                "id":"main-stream",
                                "clientId":"abu-web",
                                "configId":"popular"
                            },
                            "body":{
                                "gqlVariables":{
                                    "main":{
                                        "pagination":{
                                            "nextParams":{
                                                "count":170,
                                                "snippetCount":159,
                                                "paginationUuids":data
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "offnet":{
                            "include_lcp":True
                        },
                        "use_content_site":True,
                        "useNCP":True,
                        "useCG":True,
                        "ads":{
                            "ad_polices":True,
                            "contentType":"video/mp4,application/x-shockwave-flash",
                            "count":25,
                            "frequency":3,
                            "inline_video":True,
                            "pu":"https://tw.news.yahoo.com",
                            "se":5419954,
                            "spaceid":2144404979,
                            "start_index":1,
                            "timeout":450,
                            "type":"STRM",
                            "useHqImg":True,
                            "useResizedImages":True,
                            "enableTaboolaAds":True,
                            "taboolaConfig":{
                                "mode":"stream-twhk-news-a",
                                "placement":"taboola-stream",
                                "region":"index",
                                "targetType":"mix"
                            }
                        },
                        "batches":{
                            "pagination":True,
                            "size":159,
                            "timeout":1300,
                            "total":170
                        },
                        "enableAuthorBio":True,
                        "max_exclude":0,
                        "min_count":3,
                        "service":{
                            "specRetry":{"enabled":False}
                        },
                        "category":"",
                        "pageContext":{
                            "site":"news",
                            "section":"most-popular",
                            "topic":"default",
                            "electionPageType":"default",
                            "electionTvType":"default",
                            "pageType":"minihome",
                            "renderTarget":"default"
                        },
                        "content_type":"subsection",
                        "storeData":{
                            "stream_total":159,
                            "stream_remaining":159,
                            "stream_requested":159
                        }
                    }
                }
            },
            "context":{
                "feature":"oathPlayer,enableEvPlayer,enableGAMAds,enableGAMEdgeToEdge,videoDocking,enableRightRailGAMAds",
                "bkt":[
                    "t5-twnews-bts-p13n",
                    "t1-pc-twnews-article-rr-onegam"
                ],
                "crumb":"r4MhVhc7wAX",
                "device":"desktop",
                "intl":"tw",
                "lang":"zh-Hant-TW",
                "partner":"none",
                "prid":"1vnqestkiid1k", # 會變動的數值
                "region":"TW",
                "site":"news",
                "tz":"Asia/Taipei",
                "ver":"2.3.3197",
                "ecma":"modern"
            }
        }


        resp = requests.post(url, headers=self.session.headers, json=payload, timeout=10)
        raw = resp.text 
        data = json.loads(raw)

        items = data["g0"]["data"]["stream_items"]

        links = []
        for item in items:
            if item.get("type") != "article":
                continue  # 跳過廣告 / 影片
            
            links.append(item.get("url"))

        return links

    
    def get_all_links_len(self):
        return {
            # "chinatimes": len(self.chinatimes()),
            "ettoday": len(self.ettoday()),
            "ltn": len(self.ltn()),
            "setn": len(self.setn()),
            "tvbs": len(self.tvbs()),
            "udn": len(self.udn()),
            "yahoo": len(self.yahoo()),
        }
    
    
    def get_all_links(self):
        # links = [self.chinatimes(), self.ettoday(), self.ltn(), self.setn(), self.tvbs(), self.udn()]
        links = [self.ettoday(), self.ltn(), self.setn(), self.tvbs(), self.udn(), self.yahoo()]
        flat = [link for sub in links for link in sub]
        return flat

# 抓新聞內容
class CatchArticle:
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/"
        })  

    # soup整合包
    def _get_soup(self, url):
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError as e:
            print(f"[ERROR] {url} HTTPError:", e)
            return None
        except requests.RequestException as e:
            print(f"[ERROR] {url} RequestException:", e)
            return None

        return BeautifulSoup(resp.text, "html5lib")

    # 判斷網址是哪個的新聞網
    def fetch(self, url):
        host = urlparse(url).netloc
        if "chinatimes.com" in host:
            return self.catch_chinatimes(url)
        if "ettoday.net" in host:
            return self.catch_ettoday(url)
        if "ltn.com.tw" in host:
            return self.catch_ltn(url)
        if "setn.com" in host:
            return self.catch_setn(url)
        if "tvbs.com.tw" in host:
            return self.catch_tvbs(url)
        if "udn.com" in host:
            return self.catch_udn(url)
        if "yahoo.com" in host:
            return self.catch_yahoo(url)

    # 資料清洗
    def clean_title(self, title):
        pattern = "|".join(LABEL)

        prefix = re.compile(
            rf'^(?:[「『"“])?(?:({pattern})[／》])+'
        )
        
        t = (title or "").strip()
        t = t.replace("\u3000", " ")  # 把全形空白變成半形空白
        
        while True:
            new_t = prefix.sub("", t, count=1).lstrip()
            if new_t == t:
                break
            t = new_t

        t = re.sub(r"\s+", " ", t)
        return t
    
    # 中國時報內文 10/10 (疑似廢了)
    def catch_chinatimes(self, url):
        soup = self._get_soup(url)
        title = soup.find("h1", class_="article-title").get_text()
        title = title.replace(" ", "")
        title = self.clean_title(title)

        content = soup.find("div", class_="article-body").find_all("p", class_=False)
        texts = ""
        for word in content:
            text = word.get_text()
            if not text:
                continue

            texts += text
            
        article = {
            "source": "chinatimes",
            "url": url,
            "title": title,
            "content": texts,
        }
        
        return article

    # ETtoday內文 7/10
    def catch_ettoday(self, url):
        soup = self._get_soup(url)
        
        title = soup.find("h1", itemprop="headline").get_text()
        title = title.replace(" ", "")
        title = self.clean_title(title)
        
        content = soup.find("div", class_="story").find_all("p", class_=False)
        texts = ""  
        for word in content:
            if word.find("strong", class_=False):
                continue
            
            text = word.get_text()
            if not text:
                continue
            
            if text.startswith("記者"):
                continue
            
            texts += text
        
        article = {
            "source": "ETtoday",
            "url": url,
            "title": title,
            "content": texts,
        }
        
        return article
    
    # LTN內文 1/10 
    def catch_ltn(self, url):
        soup = self._get_soup(url)
        host = urlparse(url).netloc
        texts = ""
        
        if "ec.ltn.com.tw" in host:
            title = soup.find("h1").get_text()
            title = title.replace(" ", "")
            title = self.clean_title(title)
            
            content = soup.select('div[class="text"]')[0].find_all("p")[1:-3]
            for word in content:
                if word.find("span"):
                    continue
                
                text = word.get_text()
                
                if not text:
                    continue
                
                if "〔財經頻道／綜合報導〕" in text:
                    text = text.replace("〔財經頻道／綜合報導〕", "")
                    
                texts += text
                
            article = {
                "source": "LTN",
                "url": url,
                "title": title,
                "content": texts,
            }
            
            return article
        
        elif "news.ltn.com.tw" in host:
            title = soup.find("h1").get_text()
            title = title.replace(" ", "")
            title = self.clean_title(title)
            
            content = soup.find("div", class_="text boxTitle boxText").find_all("p")[:-2]
            for word in content:
                
                text = word.get_text()
                if text.startswith("記者") or text.startswith("首次上稿") or text.startswith("請繼續往下閱讀"):
                    continue
                
                if word.find("div", class_="image-popup-vertical-fit"):
                    continue
                
                if not text:
                    continue

                texts += text   
                
                article = {
                    "source": "LTN",
                    "url": url,
                    "title": title,
                    "content": texts,
                }
                
                return article
        
        else:
            # TODO: 是否支援其他類型的 像是sport, health
            return None
    
    # SETN內文 8/10
    def catch_setn(self, url):
        soup = self._get_soup(url)
        host = urlparse(url).netloc
        texts = ""
        
        if "www.setn.com" in host:
            title = soup.find("h1").get_text()
            title = title.replace(" ", "")
            title = self.clean_title(title)
            
            content = soup.find("article").find_all("p")
            for word in content:
                if word.find("span"):
                    continue
                
                text = word.get_text()
                
                if not text:
                    continue
                
                if "中心／" in text:
                    continue
                    
                texts += text
            
            article = {
            "source": "SETN",
            "url": url,
            "title": title,
            "content": texts,
            }
            
            return article

        elif "star.setn.com" in host:
            title = soup.find("h1").get_text()
            title = title.replace(" ", "")
            title = self.clean_title(title) 
            
            content = soup.find("article", class_="printdiv").find_all("p")
            for word in content:
                if word.find("strong", class_=False):
                    continue
                
                text = word.get_text()
                if text.startswith("記者") or text.startswith("首次上稿") or text.startswith("請繼續往下閱讀") or text.startswith("娛樂中心"):
                    continue
                
                if word.find("div", class_="image-popup-vertical-fit"):
                    continue
                
                if not text:
                    continue

                texts += text   

            article = {
                "source": "SETN",
                "url": url,
                "title": title,
                "content": texts,
            }
            
            return article
    
    # TVBS 5/10
    def catch_tvbs(self, url):
        soup = self._get_soup(url)
        texts = ""
        title = soup.find("h1", class_="title").get_text()
        title = title.replace(" ", "")
        title = self.clean_title(title)
        
        content = soup.find("div", class_="article_content")
        center = content.find("div", align="center")
        if center:
            center.decompose()
        
        texts = ""
        
        raw_text = content.get_text(separator="\n", strip=True)

        lines = [line for line in raw_text.splitlines() if line]
        texts += "".join(lines)
        texts =  texts[:-163] # TODO: 視情況再調整成成黑名單

        article = {
            "source": "TVBS",
            "url": url,
            "title": title,
            "content": texts,
        }
        
        return article
    
    # UDN內文 10/10
    def catch_udn(self, url):
        soup = self._get_soup(url)
        text = ""
        title = soup.find("h1", class_="article-content__title").get_text()
        title = title.replace(" ", "")
        title = self.clean_title(title)
        
        content = soup.find("section", class_="article-content__editor").find_all("p", class_=False, style=False)
        texts = ""
        for word in content:
            text = word.get_text()
            if not text:
                continue

            texts += text.replace("\n", "")
        
        article = {
            "source": "UDN",
            "url": url,
            "title": title,
            "content": texts,
        }
        
        return article

    
    def catch_yahoo(self, url):
        soup = self._get_soup(url)
        texts = ""
        title = soup.find("h1", class_="text-px24 text-batcave lg:text-px36 inline leading-[1.35] font-bold").get_text()
        title = title.replace(" ", "")
        title = self.clean_title(title)
        
        content = soup.find("div", class_="atoms").find_all("p")

        for word in content:
            text = word.get_text()
            if not text:
                continue
            if text.startswith("記者") or text.startswith("首次上稿") or text.startswith("請繼續往下閱讀"):
                            continue

            texts += text
            
        article = {
            "source": "yahoo",
            "url": url,
            "title": title,
            "content": texts,
        }

        return article


# 將所有的新聞存成jsonl
def download_news():
    catch_news = CatchNews()
    catch_article = CatchArticle()

    links = catch_news.get_all_links()

    filename = f"SASnews_record-{time.strftime('%Y%m%d_%H-%M-%S')}.jsonl"

    with open(filename, "w", encoding="utf-8") as f:
        i = 0
        for link in links:  # <--可調節文章數量
            i+=1
            article = catch_article.fetch(link)
            if article is None:
                continue
            if any(v == "" for v in article.values()):
                continue
        
            f.write(json.dumps(article, ensure_ascii=False) + "\n")
            print(f"{i}/{len(links)}")
    print("Download completed.  ε٩(๑> ₃ <)۶з")
    
    return filename


# download_news()


# owo = CatchNews()
# l = owo.yahoo()

# awa = CatchArticle()
# for ll in l:
#     print(awa.catch_yahoo(ll))