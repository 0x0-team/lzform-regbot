import hashlib
import time
import random
import string
import sys


def generate_challenge() -> str:
    ts = int(time.time() * 1000)
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{ts}-{rand}"


def solve(challenge: str, max_nonce: int = 100000) -> dict | None:
    prefix = challenge.encode("utf-8")
    buf_size = len(prefix) + 8

    for nonce in range(max_nonce):
        buf = bytearray(buf_size)
        buf[:len(prefix)] = prefix
        nonce_bytes = str(nonce).encode("ascii")
        buf[len(prefix):len(prefix) + len(nonce_bytes)] = nonce_bytes

        h = hashlib.sha256(buf).hexdigest()
        if h.startswith("00"):
            return {"challenge": challenge, "nonce": nonce, "hash": h}

    return None


if __name__ == "__main__":
    challenge = sys.argv[1] if len(sys.argv) > 1 else generate_challenge()
    print(f"Challenge: {challenge}")
    print("Solving...")

    t0 = time.time()
    result = solve(challenge)
    elapsed = time.time() - t0

    if result:
        print(f"Found! nonce={result['nonce']}, hash={result['hash']}, time={elapsed:.2f}s")
        print(f"_proof = {result}")
    else:
        print("Not found within limit")
