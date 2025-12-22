from catchnews import download_news
from clusternews import ClusterNews
from generatenews import GenerateNews
from readjust import rename, export_json


def main():
    # 1. 抓新聞 & 存成 jsonl
    jsonl_path = download_news()
    print(f"[1] 新聞已儲存到：{jsonl_path}")

    # 2. 分群
    clusterer = ClusterNews(batch_size=32)
    clusterer.load_jsonl(jsonl_path).fit(threshold=0.915)
    clusters = clusterer.clusters
    print(f"[2] 分群完成，共 {len(clusters)} 群")

    # 3. 生成新新聞
    generator = GenerateNews(
        model="qwen3-vl:latest",
        path=jsonl_path,
        clusters=clusters,
    )
    generator.fit()
    print("[3] 新聞生成完成σ`∀´)σ")
    
    rename()
    export_json()
    print("[4] 檔名修改完畢~")


if __name__ == "__main__":
    main()
