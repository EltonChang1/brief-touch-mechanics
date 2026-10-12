"""Inspect a bounded official HaTT subset without downloading the whole archive.

Third-party source bytes and license remain under ignored data/, never in Git.
This audits access/schema; it does not certify calibration or synchronization.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib

import numpy as np

ROOT = "https://repository.upenn.edu/server/api/core/bitstreams/"
ARCHIVE = ROOT + "dd454e74-5039-4a3c-baea-3b1894387b74/content"
LICENSE = ROOT + "6b6cc4ff-2f89-4cf0-a6ad-9a43cd6a162b/content"
MANUAL = ROOT + "bfa71546-0c44-4188-9c89-5b29c1a627c6/content"


def fetch_range(start, end=None):
    byte_range = f"bytes={start}" if end is None else f"bytes={start}-{end}"
    request = urllib.request.Request(ARCHIVE, headers={"Range": byte_range})
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 206:
            raise ValueError("Server must support range requests; refusing full archive download")
        raw = response.read()
        header = response.headers["Content-Range"]
    if start >= 0 and len(raw) != end - start + 1:
        raise ValueError("Truncated archive range")
    return raw, header


def index():
    tail, header = fetch_range(-65536)
    eocd = tail.rfind(b"PK\x05\x06")
    if eocd < 0:
        raise ValueError("Missing ZIP central directory")
    fields = struct.unpack_from("<4s4H2LH", tail, eocd)
    size, offset = fields[5], fields[6]
    directory, _ = fetch_range(offset, offset + size - 1)
    fake = directory + struct.pack("<4s4H2LH", b"PK\x05\x06", 0, 0,
                                    fields[3], fields[4], size, 0, 0)
    entries = zipfile.ZipFile(io.BytesIO(fake)).infolist()
    return entries, header


def extract(entry):
    header, _ = fetch_range(entry.header_offset, entry.header_offset + 29)
    if header[:4] != b"PK\x03\x04":
        raise ValueError("Invalid local ZIP header")
    name_len, extra_len = struct.unpack_from("<HH", header, 26)
    offset = entry.header_offset + 30 + name_len + extra_len
    raw, _ = fetch_range(offset, offset + entry.compress_size - 1)
    if entry.compress_type == zipfile.ZIP_DEFLATED:
        raw = zlib.decompress(raw, -15)
    elif entry.compress_type != zipfile.ZIP_STORED:
        raise ValueError("Unsupported archive compression")
    if len(raw) != entry.file_size or zlib.crc32(raw) != entry.CRC:
        raise ValueError("Extracted entry failed length/CRC verification")
    return raw


def inspect_xml(raw):
    root = ET.fromstring(raw)
    result = {"root_tag": root.tag, "root_attributes": root.attrib}
    for element in root:
        if not list(element):
            result[element.tag] = (element.text or "").strip()
        else:
            numbers = np.asarray([float(e.text) for e in element if e.tag == "value"])
            if numbers.size:
                result[element.tag] = {"count": int(numbers.size),
                                       "finite": bool(np.isfinite(numbers).all()),
                                       "min": float(numbers.min()), "max": float(numbers.max())}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data/hatt-audit"))
    parser.add_argument("--materials", nargs="+", default=["ABSPlastic", "Aluminum", "Book"])
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name, url in [("LICENSE.txt", LICENSE), ("MANUAL.txt", MANUAL)]:
        if not (args.out / name).exists():
            (args.out / name).write_bytes(urllib.request.urlopen(url, timeout=30).read())
    entries, header = index()
    manifest = [{"name": e.filename, "size_bytes": e.file_size, "crc32": e.CRC} for e in entries]
    (args.out / "archive-index.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    normalize = lambda s: s.lower().replace("_", "").replace(" ", "")
    requested = {normalize(m) for m in args.materials}
    matches = [e for e in entries if e.filename.lower().endswith(".xml")
               and normalize(Path(e.filename).parent.name) in requested]
    if not matches:
        raise ValueError("No matching materials; inspect archive-index.json")
    if sum(e.file_size for e in matches) > 150_000_000:
        raise ValueError("Selected subset exceeds 150 MB uncompressed safety bound")
    report = {"source": ARCHIVE, "content_range": header, "requested_materials": args.materials,
              "raw_data_redistributed": False, "measurement_gate": "not_passed",
              "unresolved": ["native channel rates", "force calibration and uncertainty",
                             "force sign/frame convention", "cross-channel timing",
                             "independent trial identity", "verified sliding"], "files": []}
    for entry in matches:
        # Flatten names; no archive-provided path is interpreted as a local destination.
        destination = args.out / Path(entry.filename).name
        raw = destination.read_bytes() if destination.exists() else extract(entry)
        if len(raw) != entry.file_size or zlib.crc32(raw) != entry.CRC:
            raise ValueError("Cached entry failed integrity check")
        destination.write_bytes(raw)
        record = {"name": entry.filename, "sha256": hashlib.sha256(raw).hexdigest(),
                  "size_bytes": len(raw), "fields": inspect_xml(raw)}
        report["files"].append(record)
        print("Audited", entry.filename, flush=True)
    (args.out / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Audit saved to {args.out / 'audit.json'}; measurement gate remains not passed")


if __name__ == "__main__":
    main()
