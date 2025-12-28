import json
from sentence_transformers import SentenceTransformer
import numpy as np


class ClusterNews:
    def __init__(self, batch_size=32):
        self.titles = []
        self.contents = []
        self.batch_size = batch_size
        self.docs = []
        self.model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        self.embeddings = None
    
    # 開啟存放新聞的 jsonl 檔案
    def load_jsonl(self, path):
        self.titles.clear()
        self.contents.clear()
        
        with open(path, "r", encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line)
                    self.contents.append(data["content"])
                    self.titles.append(data["title"])
                except json.JSONDecodeError:
                    continue
                
        return self
    
    # 前期處理，將文章儲存成正確格式
    def prework(self):
        if len(self.titles) != len(self.contents):
            raise ValueError("titles 與 contents 長度不一，資料有誤。")

        self.docs = [f"clustering: {t} {c}" for t, c in zip(self.titles, self.contents)]
        self.embeddings = self.model.encode(self.docs, convert_to_numpy=True, batch_size=32)

        return self
    
    # 計算餘弦相似性
    @staticmethod
    def cosine_sim(embeddings):
        emb_norm = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)  # 向量長度 = 矩陣 / np.linalg.norm()
        sim_matrix = emb_norm @ emb_norm.T   # (N, N)
        
        return sim_matrix
    
    # 尋找距離較近者
    @staticmethod
    def cluster(matrix, threshold=0.9):
        n = matrix.shape[0]
        visited = [False] * n
        clusters = []

        for i in range(n):
            if visited[i]:
                continue

            stack = [i]
            visited[i] = True
            cluster = []

            while stack:
                j = stack.pop()
                cluster.append(j)

                # 找所有跟 j 相似度 >= threshold 的點
                for k in range(n):
                    if k == j:
                        continue  # 跳過自己（sim=1 那格）
                    if visited[k]:
                        continue
                    if matrix[j, k] >= threshold:
                        visited[k] = True
                        stack.append(k)

            clusters.append(cluster)

        return clusters

    # 執行整個步驟
    def fit(self, threshold=0.915):
        self.prework()
        self.clusters = self.cluster(self.cosine_sim(embeddings=self.embeddings), threshold=threshold)
        
        return self
    
    # 倒出成數字的分群
    def export_num_clusters(self):
        filename = "clusters_num.txt"
        
        lines = []
        for idxs in self.clusters:
            line = " ".join(str(i) for i in idxs)  # 變成 "1 3 5"
            lines.append(line + "\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print("已輸出：", filename)
        
        return self

    # 倒出成開頭的分群
    def export_title_clusters(self):
        filename = f"clusters_str.txt"

        lines = []
        for cid, idxs in enumerate(self.clusters):
            lines.append(f"========== Cluster {cid}（共 {len(idxs)} 篇） ==========\n")
            for i in idxs:
                lines.append(f"[{i}] {self.titles[i]}\n")
            lines.append("\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print("已輸出：", filename)

        return self

    # 顯示用
    def show(self):
        print("總文章數：", len(self.contents))
        print("群數：", len(self.clusters)) 
        
        for cid, idxs in enumerate(self.clusters):
            print(f"\nCluster {cid}（共 {len(idxs)} 篇）:") 
            for i in idxs:
                print("  -", i, self.titles[i])  # 或 articles[i]["title"]

        return self


# if __name__ == "__main__":
#     path = "SASnews_record-20251221_00-19-43.jsonl"

#     clusterer = (
#         ClusterNews(batch_size=32)
#         .load_jsonl(path)
#         .fit(threshold=0.915)
#         .show()
#         .export_num_clusters()
#         .export_title_clusters
#     )
