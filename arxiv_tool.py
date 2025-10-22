import xml.etree.ElementTree as ET
import requests
from langchain_core.tools import tool

# Step1: Using Arxiv url
def search_arxiv_paper(topic: str, max_results: int =5) -> dict:

    query= "+".join(topic.lower().split())
    for char in list('()" '):
        if char in query:
            print(f"Invalid character '{char}' in query: '{query}'")
            raise ValueError(f"Cannot have character '{char}' in query: '{query}'")
    url = (
            "http://export.arxiv.org/api/query"
            f"?search_query=all:{query}"
            f"&max_results={max_results}"
            "&sortBy=submittedDate"
            "&sortOrder=descending"
        )
    print(f"Making request to ArXiv API: {url}")
    resp = requests.get(url)
    if not resp.ok:
        print(f"request failed {resp.status_code} - {resp.text}")
        raise ValueError(f"Bad response from arxiv api: {resp} \n {resp.text}")

    print(f"status code {resp.status_code}")
    # print(f"Text: {resp.text}")

    data = parse_arxiv_xml(resp.text)
    return data

def parse_arxiv_xml(xml_content: str) -> dict:
    """parse the xml content into dictionary

    Args:
        xml_content (str): xml content fetched from the arxiv api

    Returns:
        dict: parsed dictionary content
    """
    entries = []
    ns ={
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom"
    }
    root = ET.fromstring(xml_content)
    for entry in root.findall("atom:entry", ns):
        # Extract authors
        authors = [
            author.findtext("atom:name", namespaces=ns) for author in entry.findall("atom:author", ns)
        ]

        # Extract categories(term attributes)
        categories =[
            cat.attrib.get("term") for cat in entry.findall("atom:category",ns)
        ]

        # Extract pdf links (rel = 'related' and type='application/pdf')
        pdf_link= None
        for link in entry.findall("atom:link",ns):
            if link.attrib.get("type") == 'application/pdf':
                pdf_link = link.attrib.get("href")
                break

        entries.append({
            "title": entry.findtext("atom:title", namespaces=ns),
            "summary": entry.findtext("atom:summary", namespaces=ns).strip(),
            "authors": authors,
            "categories": categories,
            "pdf_link": pdf_link
        })
    return {"entries": entries}

# print(resp.text)
# print(search_arxiv_paper("transformer models", 5))


# Convert the fuctionality into tool
@tool
def arxiv_search_tool(topic: str)-> list[dict]:
    """search for recently uploaded arxiv  papers

    Args:
        topic (str): topic which u whant to search

    Returns:
        list[dict]: list of papers with their metadata
    """
    print("Calling arxiv agent")
    print(f"Searching arxiv for papers about {topic}")
    papers = search_arxiv_paper(topic=topic)
    if len(papers) == 0:
        print(f"No papers found for topic {topic}")
        raise ValueError(f"No papers found for topic {topic}")
    print(f"Found {len(papers['entries'])} paper about {topic}")
    return papers
