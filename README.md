# Syrup and Shrimp News
**A Neutral, Fair, and Objective News Source.**

💫 [Website Portal](https://syrupshrimp.qzz.io/)
⚠️ To view news results, please select > Archive (2026/01/04~2026/01/06)

- [Syrup and Shrimp News](#syrup-and-shrimp-news)
  - [Introduce](#introduce)
  - [Purpose](#purpose)
  - [Logic of Operation](#logic-of-operation)
  - [Componets](#componets)
    - [AI Model Used](#ai-model-used)
    - [News Source](#news-source)
  - [Future Updates](#future-updates)

## Introduce
We provide a news aggregation platform that helps you quickly stay informed in an age of information overload—through a neutral, objective, and fair perspective. By organizing and bringing together multiple sources, we enable you to grasp the full picture in less time and reduce information gaps caused by bias.


## Purpose
In today’s information environment, access to international news is often shaped by media bias and one-sided narratives. Public understanding of global affairs is also frequently constrained by information overload and limited source diversity. To address this challenge, we plan to build an AI-powered news aggregation platform. The platform will systematically collect news content from a wide range of sources worldwide and use intelligent analysis and fact-checking to reduce bias and perspective-driven storytelling. It will integrate and present information in an objective, data-driven manner. Our goal is to provide a trustworthy and neutral news perspective that helps readers gain a more comprehensive understanding of international events, while strengthening media literacy and critical thinking.


## Logic of Operation
We first crawl trending news from major news websites. Next, we use **nomic-embed-text** to embed and cluster all articles. Then, we feed the clustered results into **qwen3-vl:8b** to generate a new, objective and neutral synthesized article. Finally, we upload the generated content to our news platform.

![image](https://github.com/Syrup2718/Syrup_and_Shrimp_News/blob/main/images/SASN.png)



## Componets
### AI Model Used

1. [Nomic-Embed-Text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
  \- cluster news
2. [Qwen3-vl:8b](https://ollama.com/library/qwen3-vl)
  \- generate news
3. [Qwen3-vl:4b](https://ollama.com/library/qwen3-vl)
  \- detection and generate news

### News Source
1. [LTN](https://www.ltn.com.tw/)
2. [Yahoo](https://tw.news.yahoo.com/)
3. [TVBS](https://www.tvbs.com.tw/)
4. [ETtoday](https://www.ettoday.net/)
5. [SETN](https://www.setn.com/)
6. [UDN](https://udn.com/news/index)
7. ~~[Chinatimes](https://www.chinatimes.com/?chdtv)~~


## Future Updates
1. Support additional news sources to improve cross-media comparison.
2. Introduce a "digest mode" for quick event understanding.
3. Enhance clustering accuracy with temporal and semantic constraints.
4. Add multilingual support for news summarization.
5. Improve website UI and user interaction features.
