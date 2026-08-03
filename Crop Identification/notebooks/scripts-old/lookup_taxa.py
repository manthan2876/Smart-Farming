import urllib.request, json, time

HEADERS = {"User-Agent": "Mozilla/5.0"}
queries = [
    ("Gossypium hirsutum", "Cotton"),
    ("Arachis hypogaea",   "Groundnut"),
    ("Solanum tuberosum",  "Potato"),
    ("Solanum lycopersicum","Tomato"),
    ("Capsicum frutescens", "Chilli"),
]
for q, label in queries:
    url = "https://api.inaturalist.org/v1/taxa?q=" + q.replace(" ", "+")
    req = urllib.request.Request(url, headers=HEADERS)
    d   = json.loads(urllib.request.urlopen(req).read())
    r   = d["results"][0]
    print(f'{label}: id={r["id"]} name={r["name"]} obs={r.get("observations_count",0)}', flush=True)
    time.sleep(0.5)
