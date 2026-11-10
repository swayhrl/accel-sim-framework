"""Read-only metadata scout for the 2026-11-10 AI-ARCH survey.

Uses public arXiv Atom and OpenAlex APIs. It does not fetch models or data.
"""
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

QUERIES = {
    "3dgs_systems": 'all:"Gaussian Splatting" AND (all:training OR all:system)',
    "3dgs_memory": 'all:"Gaussian Splatting" AND (all:memory OR all:offload)',
    "moe_offload": 'all:"mixture of experts" AND (all:offload OR all:heterogeneous)',
    "moe_routing": 'all:"mixture of experts" AND (all:routing OR all:prefetch)',
    "hybrid_kv": 'all:"hybrid attention" AND (all:cache OR all:inference)',
    "linear_attention": 'all:"linear attention" AND (all:state OR all:cache)',
    "kv_systems": 'all:"KV cache" AND (all:memory OR all:offload)',
    "sparse_training": 'all:"sparse convolution" AND (all:training OR all:GPU)',
    "rl_systems": 'all:"reinforcement learning" AND (all:rollout OR all:training) AND all:system',
    "video_dit": 'all:"video diffusion" AND (all:cache OR all:system)',
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "AI-ARCH-literature-review/1.0 (public metadata)"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()


def arxiv(query, limit=15):
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": query, "start": 0, "max_results": limit,
        "sortBy": "submittedDate", "sortOrder": "descending",
    })
    root = ET.fromstring(fetch(url))
    ns = "{http://www.w3.org/2005/Atom}"
    rows = []
    for e in root.findall(ns + "entry"):
        rows.append({
            "title": " ".join((e.findtext(ns + "title") or "").split()),
            "url": e.findtext(ns + "id"),
            "published": e.findtext(ns + "published"),
            "updated": e.findtext(ns + "updated"),
            "abstract": " ".join((e.findtext(ns + "summary") or "").split()),
        })
    return {"query": query, "api_url": url, "results": rows}


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        with open(sys.argv[2], encoding="utf-8-sig") as source:
            saved = json.load(source)
        for key, block in saved.items():
            print("\n" + key)
            for i, paper in enumerate(block.get("results", []), 1):
                print(i, paper["published"][:10], paper["title"], paper["url"])
        return
    output = {}
    for key, query in QUERIES.items():
        try:
            output[key] = arxiv(query)
            print(key, len(output[key]["results"]), file=sys.stderr)
        except Exception as exc:
            output[key] = {"query": query, "error": f"{type(exc).__name__}: {exc}"}
            print(key, "ERROR", str(exc), file=sys.stderr)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
