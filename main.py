import sys, json, time, hashlib, string, random, asyncio
import httpx

CAPTCHA_ID = "9ee5ee5715144aca98e58280f20334fe"
SOLVER_URL = "https://gtv4.c0ffee.space"
BASE_URL = "https://form.lztech.top"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def pow_solve(max_nonce=100000):
    ts = int(time.time() * 1000)
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    challenge = f"{ts}-{rand}"
    prefix = challenge.encode()
    buf = bytearray(len(prefix) + 8)
    buf[:len(prefix)] = prefix
    for nonce in range(max_nonce):
        b = bytearray(buf)
        nb = str(nonce).encode("ascii")
        b[len(prefix):len(prefix) + len(nb)] = nb
        if hashlib.sha256(b).hexdigest().startswith("00"):
            return {"challenge": challenge, "nonce": nonce}
    return {"challenge": challenge, "nonce": 0}


def rand_email():
    name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 16)))
    domains = ["gmail.com", "outlook.com", "qq.com", "163.com", "yahoo.com", "proton.me", "icloud.com"]
    return f"{name}@{random.choice(domains)}"


def rand_password(min_len=10, max_len=16):
    length = random.randint(min_len, max_len)
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choices(chars, k=length))


async def register_one(client: httpx.AsyncClient, email, password, display_name="", referer=""):
    ref = referer or f"{BASE_URL}/auth/login"

    r = await client.get(f"{SOLVER_URL}/solve", params={"captcha_id": CAPTCHA_ID, "referer": ref})
    r.raise_for_status()
    data = r.json()
    proof = pow_solve()

    body = {
        "email": email,
        "password": password,
        "displayName": display_name or email.split("@")[0],
        "geetestResult": data["geetestResult"],
        "_proof": proof,
    }
    return await client.post(
        f"{BASE_URL}/api/auth/register",
        json=body,
        headers={"User-Agent": UA, "Referer": ref},
    )


async def _worker(sem, idx, total, email, password, name, ref):
    async with sem:
        print(f"[{idx}/{total}] {email} ... ", end="", flush=True)
        t0 = time.time()
        resp = None
        try:
            async with httpx.AsyncClient(timeout=60) as c:
                resp = await register_one(c, email, password, name, ref)
            elapsed = time.time() - t0
            if resp.status_code == 201:
                print(f"201 ({elapsed:.1f}s)")
                return True
            print(f"{resp.status_code} ({elapsed:.1f}s) {resp.text[:200]}")
            return False
        except Exception as e:
            elapsed = time.time() - t0
            body = resp.text[:200] if resp is not None and hasattr(resp, "text") else "N/A"
            print(f"ERR ({elapsed:.1f}s) {e} | body={body}")
            return False


async def batch(count, workers=3, ref=""):
    sem = asyncio.Semaphore(workers)
    tasks = []
    for i in range(1, count + 1):
        email = rand_email()
        tasks.append(_worker(sem, i, count, email, rand_password(), email.split("@")[0], ref))
    results = await asyncio.gather(*tasks)
    ok = sum(1 for r in results if r)
    print(f"\nDone: {ok} success, {count - ok} failed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  uv run python main.py <count> [workers]          # batch")
        print("  uv run python main.py <email> <password>         # single")
        exit(1)

    if "@" in sys.argv[1]:
        email = sys.argv[1]
        pwd = sys.argv[2] if len(sys.argv) > 2 else "test1234"
        name = sys.argv[3] if len(sys.argv) > 3 else ""
        ref = sys.argv[4] if len(sys.argv) > 4 else ""
        t0 = time.time()
        try:
            resp = httpx.post(
                f"{BASE_URL}/api/auth/register",
                json={"email": email, "password": pwd, "displayName": name or email.split("@")[0],
                      "geetestResult": httpx.get(f"{SOLVER_URL}/solve", params={"captcha_id": CAPTCHA_ID, "referer": ref or f"{BASE_URL}/auth/login"}).json()["geetestResult"],
                      "_proof": pow_solve()},
                headers={"User-Agent": UA, "Referer": ref or f"{BASE_URL}/auth/login"},
                timeout=60,
            )
            elapsed = time.time() - t0
            print(f"HTTP {resp.status_code} ({elapsed:.1f}s)")
            print(resp.text[:600] if resp.status_code != 201 else resp.text[:300])
        except Exception as e:
            elapsed = time.time() - t0
            print(f"ERR ({elapsed:.1f}s) {e}")
        exit(0)

    count = int(sys.argv[1])
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    ref = sys.argv[3] if len(sys.argv) > 3 else ""
    asyncio.run(batch(count, workers, ref))
