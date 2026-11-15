"""Local controller for the RunPod GPU pod: create, upload, exec, tail, download, terminate. Token and pod id are kept in /tmp/podstate.json (never printed)."""
import base64, json, os, secrets, sys, time, urllib.request, concurrent.futures as cf
ST = "/tmp/podstate.json"; GQL = "https://api.runpod.io/graphql"
def gql(q):
    r = urllib.request.Request(GQL, json.dumps({"query": q}).encode(), {"content-type": "application/json"}); d = json.load(urllib.request.urlopen(r, timeout=60))
    if d.get("errors"): raise RuntimeError(json.dumps(d["errors"])[:600])
    return d["data"]
def state(): return json.load(open(ST))
def create(gpu="NVIDIA GeForce RTX 3090", disk=60):
    token = secrets.token_hex(16); agent = base64.b64encode(open(os.path.join(os.path.dirname(__file__), "pod_agent.py"), "rb").read()).decode()
    args = f"bash -c 'echo {agent} | base64 -d > /agent.py; python3 /agent.py'"
    q = '''mutation { podFindAndDeployOnDemand(input: { cloudType: ALL, gpuCount: 1, gpuTypeId: "%s", name: "splitjepa-robot", imageName: "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04",
      containerDiskInGb: %d, volumeInGb: 0, minVcpuCount: 8, minMemoryInGb: 24, ports: "8000/http", dockerArgs: %s, env: [{key: "AGENT_TOKEN", value: "%s"}] }) { id costPerHr machine { gpuDisplayName } } }''' % (gpu, disk, json.dumps(args), token)
    d = gql(q)["podFindAndDeployOnDemand"]; json.dump({"id": d["id"], "token": token}, open(ST, "w")); print("pod", d["id"], d["machine"]["gpuDisplayName"], d["costPerHr"], "$/h")
def url(p): return f"https://{state()['id']}-8000.proxy.runpod.net{p}"
def req(method, path, data=None, timeout=120):
    r = urllib.request.Request(url(path), data, {"X-Token": state()["token"], "Content-Type": "application/octet-stream", "User-Agent": "curl/8.5.0"}, method=method); return urllib.request.urlopen(r, timeout=timeout).read()
def wait_up(maxs=600):
    t = time.time()
    while time.time() - t < maxs:
        try: req("GET", "/", timeout=15); print("agent up after", int(time.time() - t), "s"); return
        except Exception: time.sleep(10)
    raise SystemExit("agent not reachable")
def exec_(cmd, bg=False, log="logs/last.log", timeout=80):
    out = req("POST", "/exec", json.dumps({"cmd": cmd, "bg": bg, "log": log, "timeout": timeout}).encode(), timeout=timeout + 20); return json.loads(out)
def tail(path, n=3000): return req("GET", f"/tail?path={path}&n={n}").decode(errors="replace")
def upload(local, remote, chunk=24 << 20, workers=4):
    size = os.path.getsize(local); offs = list(range(0, size, chunk)); req("PUT", f"/upload?path={remote}&offset=0", b"")
    def one(o):
        with open(local, "rb") as f: f.seek(o); b = f.read(chunk)
        for k in range(5):
            try: req("PUT", f"/upload?path={remote}&offset={o}", b, timeout=300); return
            except Exception as e: time.sleep(3)
        raise RuntimeError(f"chunk {o} failed")
    with cf.ThreadPoolExecutor(workers) as ex: list(ex.map(one, offs))
    got = json.loads(req("GET", f"/size?path={remote}"))["size"]; assert got == size, (got, size); print("uploaded", remote, size >> 20, "MB")
def download(remote, local, chunk=24 << 20):
    size = json.loads(req("GET", f"/size?path={remote}"))["size"]; os.makedirs(os.path.dirname(local) or ".", exist_ok=True)
    with open(local, "wb") as f:
        for o in range(0, size, chunk): f.write(req("GET", f"/download?path={remote}&offset={o}&length={chunk}", timeout=300))
    print("downloaded", local, size)
def terminate():
    gql('mutation { podTerminate(input: {podId: "%s"}) }' % state()["id"]); print("terminated", state()["id"])
def pods(): return gql("query { myself { pods { id desiredStatus costPerHr runtime { uptimeInSeconds } } clientBalance } }")["myself"]
if __name__ == "__main__":
    c = sys.argv[1]
    if c == "create": create(*sys.argv[2:3])
    elif c == "up": wait_up()
    elif c == "exec": print(exec_(sys.argv[2], bg=len(sys.argv) > 3 and sys.argv[3] == "bg", timeout=int(os.environ.get("T", 80)))["out"] if not (len(sys.argv) > 3 and sys.argv[3] == "bg") else exec_(sys.argv[2], bg=True, log=sys.argv[4] if len(sys.argv) > 4 else "logs/last.log"))
    elif c == "tail": print(tail(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3000))
    elif c == "upload": upload(sys.argv[2], sys.argv[3])
    elif c == "download": download(sys.argv[2], sys.argv[3])
    elif c == "terminate": terminate()
    elif c == "pods": print(json.dumps(pods(), indent=1))
