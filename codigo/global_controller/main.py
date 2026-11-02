import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone
import uvicorn

app = FastAPI(title="Genomics Distributed Cluster Master (Real Mode)")

UPLOAD_DIR = "data_input"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# CONFIGURA AQUÍ LAS URLs REALES DE TUS WORKERS
# Si usas Tailscale, aquí van las IPs 100.x.x.x
clusters = {
    "worker-1-china": {
        "cluster_id": "worker-1-china",
        "region": "singapore",
        "url": "https://worker-1-china.fly.dev", 
        "specs": {"cpu": 8, "ram": "32GB"},
        "status": "online"
    },
    "worker-europe-czech": {
        "cluster_id": "worker-europe-czech",
        "region": "czech-republic",
        "url": "http://100.101.102.2:8750", 
        "specs": {"cpu": 4, "ram": "16GB"},
        "status": "online"
    },
    "worker-latam-azure": {
        "cluster_id": "worker-latam-azure",
        "region": "mexico-central",
        "url": "http://100.101.102.3:8750", 
        "specs": {"cpu": 2, "ram": "8GB"},
        "status": "online"
    }
}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return r"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Orquestador Multi-Cloud Real</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        body { background-color: #070b14; color: #e2e8f0; }
        .glass-panel { background: rgba(15, 23, 42, 0.82); backdrop-filter: blur(12px); border: 1px solid rgba(51, 65, 85, 0.6); }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; background-color: #10b981; }
    </style>
</head>
<body class="p-8">
    <header class="glass-panel p-6 rounded-2xl mb-8 flex justify-between items-center border border-cyan-500/30">
        <h1 class="text-2xl font-bold text-white"><i class="fa-solid fa-dna text-cyan-400 mr-2"></i> CLÚSTER MULTI-CLOUD REAL</h1>
        <button onclick="startRealJob()" class="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 rounded-xl font-bold text-sm">
            <i class="fa-solid fa-play mr-2"></i> DISPARAR ANÁLISIS REAL
        </button>
    </header>
    <div class="grid grid-cols-3 gap-6 mb-8" id="real-workers-grid"></div>
    <div class="glass-panel p-6 rounded-2xl">
        <h3 class="font-bold text-cyan-400 mb-2">Telemetría de Red</h3>
        <div id="realLog" class="bg-slate-950 p-4 rounded-xl font-mono text-xs text-green-400 h-64 overflow-y-auto space-y-1"></div>
    </div>
    <script>
        async function fetchStatus() {
            const res = await fetch('/status');
            const data = await res.json();
            const grid = document.getElementById('real-workers-grid');
            grid.innerHTML = Object.values(data.active_nodes).map(n => `
                <div class="glass-panel p-5 rounded-2xl border-t-4 border-t-cyan-400">
                    <h3 class="font-bold text-lg text-white">${n.cluster_id}</h3>
                    <p class="text-xs text-slate-400 truncate">Endpoint: <code>${n.url}</code></p>
                </div>`).join('');
        }
        function log(msg) { document.getElementById('realLog').innerHTML += `<div>[${new Date().toLocaleTimeString()}] ${msg}</div>`; }
        async function startRealJob() {
            log("🚀 Iniciando despacho real...");
            const res = await fetch('/start_real_job', { method: 'POST' });
            const data = await res.json();
            data.results.forEach(r => log(r.success ? `✅ ${r.worker}: ${JSON.stringify(r.response)}` : `⚠️ ${r.worker}: ${r.error}`));
        }
        setInterval(fetchStatus, 3000);
        fetchStatus();
    </script>
</body>
</html>"""

@app.get("/status")
async def status():
    return {"active_nodes": list(clusters.values())}

@app.post("/start_real_job")
async def start_real_job():
    results = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for cid, node in clusters.items():
            try:
                # Asegúrate de que el Worker tenga este endpoint /process
                resp = await client.post(f"{node['url']}/process", json={"task": "adn", "size": 20})
                results.append({"worker": cid, "success": True, "response": resp.json()})
            except Exception as e:
                results.append({"worker": cid, "success": False, "error": str(e)})
    return {"status": "dispatched", "results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)