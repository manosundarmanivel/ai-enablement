import json
import requests
from bs4 import BeautifulSoup

MAX_TEXT_SIZE = 5000

def get_url(event):
    params = event.get("parameters", [])
    for p in params:
        if isinstance(p, dict) and p.get("name") == "url":
            return p.get("value")
    raise ValueError(f"URL not found in parameters: {params}")

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return text[:MAX_TEXT_SIZE]

def lambda_handler(event, context):
    print("FULL EVENT:", json.dumps(event))

    try:
        url = get_url(event)
        print("Crawling URL:", url)

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text

        cleaned_text = clean_html(html)
        cleaned_text = cleaned_text.encode("utf-8", errors="ignore").decode("utf-8")

        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup", ""),
                "function": event.get("function", ""),
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "contentType": "TEXT",
                            "body": cleaned_text
                        }
                    }
                }
            }
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup", ""),
                "function": event.get("function", ""),
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "contentType": "TEXT",
                            "body": f"Error while scraping: {str(e)}"
                        }
                    }
                }
            }
        }
