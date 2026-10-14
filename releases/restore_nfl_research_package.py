from pathlib import Path
import hashlib, json
root = Path(__file__).resolve().parent
manifest = json.loads((root / "NFL_Research_Package_Parts.json").read_text())
chunks = []
for part in manifest["parts"]:
    chunk = (root / part["name"]).read_bytes()
    if len(chunk) != part["size"] or hashlib.sha256(chunk).hexdigest() != part["sha256"]:
        raise ValueError("Invalid archive part: " + part["name"])
    chunks.append(chunk)
data = b"".join(chunks)
if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
    raise ValueError("Archive checksum mismatch")
output = root / manifest["output"]
output.write_bytes(data)
print("Restored:", output)
