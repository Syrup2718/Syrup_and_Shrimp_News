import ollama
import json
import os 
import datetime
import re

time = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))

BAD_STRS = [
    "作為AI", "作為一個AI模型", "作为AI", "作为一个AI模型",
    "台灣是中國",
    "台湾是中国",
    "多源報導",
    "主觀",
    "避免情緒化",
    "觀客" ,
    "客觀" ,
    "不作價值判斷",
]


class GenerateNews:
    def __init__(self, model, path, clusters):
        self.model = model
        self.path = path
        self.clusters = clusters
        self.clusters = self._min_cluster(self.clusters)
        
        self.articles = []
        self.title = []
        self.body = []
        
        ollama.pull(model)
    
    
    @staticmethod
    def _min_cluster(clusters):
        min_cluster = []
        for cluster in clusters:
            if len(cluster) > 1:
                min_cluster.append(cluster)
                
        return min_cluster
    
    
    def load_articles(self, cluster):
        self.articles.clear()
        with open(self.path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=0):  # idx 從 1 開始
                if idx in cluster:
                    try:
                        obj = json.loads(line)
                        self.articles.append(obj)
                    except json.JSONDecodeError:
                        print(f"第 {idx} 行 JSON 壞掉，略過")
        
        return self
    
    
    def build_prompt(self):
        max_char = 4096
        total_len=0
        blocks = []
        for i, art in enumerate(self.articles, start=1):
            title = art.get("title", "").strip()
            content = art.get("content", "").strip()
            chunk = (
            f"【原始新聞 {i} 標題】{title}\n"
            f"【原始新聞 {i} 內文】{content}\n\n"
            )

            if total_len + len(chunk) > max_char:
                break
            blocks.append(chunk)
            total_len += len(chunk)
        
        joined = "\n\n".join(blocks)
        
        prompt = f"""
            你是專業的新聞編輯，負責把多家媒體對同一事件的報導整合成一篇中立、客觀、清晰的新聞。

            請你依照以下要求進行：
            1. 先閱讀我提供的多篇原始報導。
            2. 整理出一篇新的新聞稿（不要抄原文句子，要重新撰寫）。
            3. 報導要中立、客觀、避免情緒性字眼。
            4. 請使用繁體中文撰寫。
            5. 勿用過多的冗詞贅字，聚焦於事件本身。
            6. 請以Inverted pyramid結構寫作。
            7. 不評論，只報導。
            8. 標題不要超過20字。

            輸出格式非常重要，請嚴格遵守：
            - 第一行：新聞標題（一行，不要額外前綴）
            - 第二行以後：新聞內文（可多段，用換行分段）

            以下是原始新聞資料：

            {joined}
            """
            
        # print(len(prompt))
        # print(prompt)
        # print("===========================================================")
        
        return prompt.strip()
    
    
    @staticmethod
    def _is_bad(text):
        for line in text.splitlines():
            stripped = line.lstrip()

            # 標題：#、##、### ...
            if stripped.startswith("#"):
                return True

            # 項目符號：- * +
            if stripped.startswith(("-", "*", "+")):
                return True

            # 編號清單：1. 2. 3.
            if re.match(r"\d+\.\s", stripped):
                return True
        
        if "```" in text or "**" in text or "__" in text or "`" in text:
            return True
        
        # 1. 不能有 LaTeX
        if "\\boxed{" in text or "\\begin{" in text or "$" in text:
            return True

        # 2. 不能有大量非中英符號（例如阿拉伯文）
        if re.search(r"[\u0600-\u06FF]", text):  # Arabic range
            return True

        # 3. 禁止特定政治 / AI 聲明句
        for s in BAD_STRS:
            if s in text:
                return True

        return False
    
    
    def generate(self):
        for attempt in range(3):
            prompt = self.build_prompt()
            
            response = ollama.chat(
                model = self.model,
                messages=[
                    {"role": "system", "content": "你是一位專業且中立的新聞編輯。"},
                    {"role": "user", "content": prompt},
                ],
            )
            
            raw_output = response["message"]["content"].strip()
            
            if not self._is_bad(raw_output):
                break  # OK 了
            
            print(f"[WARN] 生成結果不符合規範，第 {attempt+1} 次重試")

        else:
            # 三次都失敗，就直接放棄這個 cluster
            raise ValueError(f"這組prompt有問題\n{prompt}")
        
        
        lines = raw_output.splitlines()
        if not lines:
            raise ValueError("空空")
        
        first_line = lines[0].strip()
        
        # 去掉可能的 markdown 標題符號
        if first_line.startswith("#"):
            first_line = first_line.lstrip("#").strip()
        
        self.title = first_line
        self.body = "\n".join(lines[1:]).strip()  # 第二行之後當作內文

        return self
    
    
    def export_news(self, filename=None):
        dir = f".\\articles\{time.strftime('%Y%m%d')}"
        os.makedirs(dir, exist_ok=True)
        
        if filename is None:
            safe_title = "".join(c for c in self.title if c not in r'\/:*?"<>|').strip()
            if not safe_title:
                safe_title = "article"
            filename = safe_title + ".txt"
        
        path = os.path.join(dir, filename)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.title + "\n")
            f.write(self.body + "\n")

        return self

    
    def fit(self):
        for idx, cluster in enumerate(self.clusters):
            self.load_articles(cluster)
            self.generate()
            self.export_news()
            print(f"目前進度 {idx+1}/{len(self.clusters)}")
        
        return self


# owo = GenerateNews(model="qwen3-vl:latest", path="SASnews_record-20251213_14-17-49.jsonl", clusters=[[0, 274, 203, 161, 131, 78], [1, 65, 209, 142], [2], [3], [4, 321, 108], [5, 181], [6], [7, 159], [8], [9], [10, 241, 111], [11], [12], [13, 311], [14], [15, 260, 224, 158]])
# owo.fit()



