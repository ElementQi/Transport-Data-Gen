from concurrent.futures import ThreadPoolExecutor, as_completed
from chroma_langchain.splitters import ClusterSemanticSplitter
from langchain_openai import OpenAIEmbeddings
import json
from tqdm import tqdm
import pandas as pd
import time

content_path = "../air_travel/data/content.xlsx"
content_df = pd.read_excel(content_path)

# Extract title and content
content = content_df[["title", "content"]]
text = content.content
titles = content.title
content_list = text.to_list()

# Initialize the embedding function
embed = OpenAIEmbeddings(
    base_url="https://one-api.s.metames.cn:38443/v1",
    api_key="xxx",
    model="text-embedding-3-small",
)

# Function to split text and get embeddings


def process_content(single_content):
    cluster_ts = ClusterSemanticSplitter(embedding_function=embed)
    for attempt in range(3):  # max 3 times
        try:
            chunked_content = cluster_ts.split_text(single_content)
            filtered_content = list(filter(lambda x: len(x) > 5, chunked_content))
            return filtered_content if filtered_content else [""]  # avoid empty slicing
        except Exception as e:
            print(f"Error processing content: {single_content[:20]}... - {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                return []


# Use ThreadPoolExecutor for multi-threading
cluster_chunked_content_list = []
with ThreadPoolExecutor(max_workers=3) as executor:
    future_to_content = {executor.submit(process_content, single_content): single_content for single_content in content_list}
    
    for future in tqdm(
        as_completed(future_to_content),
        total=len(content_list),
        ):
        chunked_content = future.result()
        cluster_chunked_content_list.append(chunked_content)

        # Save intermediate results to JSON
        title_context_pairs = []
        for title, context_list in zip(titles, cluster_chunked_content_list):
            for context in context_list:
                if context:
                    title_context_pairs.append({"instruction": title, "output": context})

        with open("title_context_pairs_partial.json", "w", encoding="utf-8") as json_file:
            json.dump(title_context_pairs, json_file, indent=4, ensure_ascii=False)

# Final save to JSON
with open("title_context_pairs.json", "w", encoding="utf-8") as json_file:
    json.dump(title_context_pairs, json_file, indent=4, ensure_ascii=False)
