import sys, json, time, hashlib, string, random
import httpx

CAPTCHA_ID = "9ee5ee5715144aca98e58280f20334fe"
SOLVER_URL = "https://gtv4.c0ffee.space"
BASE_URL = "https://form.lztech.top"


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


def register_one(email, password, display_name="", referer=""):
    ref = referer or f"{BASE_URL}/auth/login"
    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    with httpx.Client(timeout=60) as c:
        r = c.get(f"{SOLVER_URL}/solve", params={"captcha_id": CAPTCHA_ID, "referer": ref})
        r.raise_for_status()
        data = r.json()
        gres = data["geetestResult"]
        proof = pow_solve()

        body = {
            "email": email,
            "password": password,
            "displayName": display_name or email.split("@")[0],
            "geetestResult": gres,
            "_proof": proof,
        }
        resp = c.post(
            f"{BASE_URL}/api/auth/register",
            json=body,
            headers={"User-Agent": ua, "Referer": ref},
        )
        return resp


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  uv run python main.py <count>              # batch")
        print("  uv run python main.py <email> <password>   # single")
        exit(1)

    # single mode: email contains @, or count == 1 with email as 2nd arg
    if "@" in sys.argv[1]:
        email = sys.argv[1]
        pwd = sys.argv[2] if len(sys.argv) > 2 else "test1234"
        name = sys.argv[3] if len(sys.argv) > 3 else ""
        ref = sys.argv[4] if len(sys.argv) > 4 else ""
        t0 = time.time()
        resp = register_one(email, pwd, name, ref)
        elapsed = time.time() - t0
        print(f"HTTP {resp.status_code} ({elapsed:.1f}s)")
        print(resp.text[:600] if resp.status_code != 201 else resp.text[:300])
        exit(0)

    count = int(sys.argv[1])
    results = {"success": 0, "failed": 0, "errors": []}
    print(f"Batch registering {count} accounts...\n")

    for i in range(1, count + 1):
        email = rand_email()
        pwd = rand_password()
        name = email.split("@")[0]
        print(f"[{i}/{count}] {email} ... ", end="", flush=True)
        t0 = time.time()
        try:
            resp = register_one(email, pwd, name)
            elapsed = time.time() - t0
            if resp.status_code == 201:
                results["success"] += 1
                print(f"201 ({elapsed:.1f}s)")
            else:
                results["failed"] += 1
                print(f"{resp.status_code} ({elapsed:.1f}s) {resp.text[:80]}")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append((email, str(e)))
            print(f"ERR ({time.time()-t0:.1f}s) {e}")

    print(f"\nDone: {results['success']} success, {results['failed']} failed")
