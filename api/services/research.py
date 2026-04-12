import os
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from openai import OpenAI
import trafilatura

# Load environment variables
load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Research:
    def __init__(self):
        # Initialize Google Search wrapper
        self.search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def find_webpages(self, query, limit=5):
        """
        Return top 'limit' webpage URLs for a given query
        """
        try:
            results = self.search.results(query)

            if isinstance(results, dict) and "organic_results" in results:
                return [
                    res.get("link")
                    for res in results["organic_results"]
                    if res.get("link")
                ][:limit]

            return []

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def read_html(self, url, char_limit=5000):
        try:
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded)

            if not text:
                return ""

            content = self.summarise_page(text[:char_limit])
            return {"url": url, "content": content}

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def summarise_page(self, content):
        """
        Summarise given text content using OpenAI
        """
        if not content:
            return "No content to summarise."

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarise the following content concisely:\n\n{content}"
                    }
                ],
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"OpenAI error: {e}")
            return "Error generating summary."


# =========================
# TEST SCRIPT
# =========================
# if __name__ == "__main__":
#     researcher = Research()

#     query = "what is OCBC Bank's strategy for digital transformation?"
#     print(f"\nSearching for: {query}\n")

#     urls = researcher.find_webpages(query)

#     if not urls:
#         print("No URLs found.")
#         exit()

#     for i, url in enumerate(urls, start=1):
#         print(f"[{i}] URL: {url}")

#         content = researcher.read_html(url, char_limit=10000)

#         if not content:
#             print("No content extracted.\n" + "-" * 50)
#             continue

#         summary = researcher.summarise_page(content)

#         print(f"\nSummary:\n{summary}")
#         print("\n" + "-" * 70 + "\n")