from datetime import datetime, timezone
import secrets
crockford: str = "0123456789ABCDEFGHJKLMNPQRSTVWXYZ"


def base32(b: bytes) -> str:
    num = int.from_bytes(b, byteorder="big")
    ch = []
    for _ in range(26):
        ch.append(crockford[num & 31])
        num >>= 5
    return ''.join(ch[::-1])


def ulid() -> str:
    timestamp = int(datetime.now(timezone.utc).timestamp()*1000)
    epoch = timestamp.to_bytes(6, byteorder="big")
    rand = secrets.token_bytes(10)
    return base32(epoch+rand)