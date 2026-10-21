"""Digest-gated replay of authentic NTL 1.5 C random-integer semantics.

The historical source is supplied by the operator, never redistributed here.
The offline receipt checks recorded observations; only --archive executes C.
Neither mode attributes this software to the designers of P-521.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile

M = (1 << 107) - 1
A = pow(3, 121, M)
ARCHIVE_SHA256 = "c2d80c5293c824b16f89ac7e5e0aeb29e3996f8560b877c44858f41c43717e1c"
ARCHIVE_BYTES = 446513
ARCHIVE_URL = "https://web.archive.org/web/19970801214429id_/http://www.cs.wisc.edu/~shoup/ntl/ntl-1.5.tar.Z"
MEMBERS = {
    "lip.c": "3fe2f59879c2dbc57fa5e324676cf5d56dc21176030b93e4b11eeb808864cde2",
    "lip.h": "578173101d0469f0a36c97dee8b876e1f32766dcd7c809ee290a2ae306b8a14c",
    "MakeDesc.c": "cf6fa9b7239373c26d8f04c1086ee1108ddf87a1a75e826c387f15fe57be06d4",
    "MakeDescAux.c": "907258ae48d71a92c5e125e141fd96f6b136f0d4e9658b8b3fa61b795e95de1a",
    "IsFinite.c": "31c3b45f150376cfac3eb35dfe0c40422a582b39c6372713b582f6bf0c496582",
    "IsFinite.h": "8735b1480de73447dadbcc158170e44fe342442d60fdf4435c9185b3c64faf8b",
}
FLAGS = ["-std=gnu89", "-O2", "-fwrapv"]
WIDTHS = (26, 30, 50)
NATIVE_CONFIG_SHA256 = "f07bd4d2164b916c85685fbedf6632bf1c1e05104a6caa7fd5f3d21e4d03ca3d"

# This new driver calls the unchanged historical implementation. Including lip.c
# makes its private state visible for observation without instrumenting it.
DRIVER = r'''
#include "lip.c"

static void decimal(const char *s, verylong *v) {
    int negative = *s == '-';
    if (negative || *s == '+') ++s;
    zintoz(0, v);
    for (; *s; ++s) {
        if (*s < '0' || *s > '9') exit(3);
        zsmul(*v, 10, v);
        zsadd(*v, *s-'0', v);
    }
    if (negative) znegate(v);
}

static void limbs(verylong v, int nullable) {
    long i, n = v ? v[0] : 0;
    if (!v && nullable) { printf("null"); return; }
    printf("[%ld", n);
    if (n < 0) n = -n;
    for (i=1; i<=n; ++i) printf(",%ld", v[i]);
    printf("]");
}

int main(int argc, char **argv) {
    verylong seed=0, arg=0, value=0;
    if (argc != 4) return 2;
    if (strcmp(argv[2], "*") != 0) {
        decimal(argv[2], &seed);
        zrstart(seed);
    }
    decimal(argv[3], &arg);
    if (strcmp(argv[1], "draw") == 0)
        zintoz(zrandom(ztoint(arg)), &value);
    else if (strcmp(argv[1], "bnd") == 0)
        zrandomb(arg, &value);
    else if (strcmp(argv[1], "len") == 0)
        zrandoml(ztoint(arg), &value);
    else return 2;
    printf("{\"width\":%d,\"value\":", ZZ_NBITS);
    limbs(value, 0);
    printf(",\"state\":");
    limbs(zseed, 1);
    printf("}\n");
    return 0;
}
'''


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def authenticate_archive(path):
    """Authenticate compressed bytes before decompression or source execution."""
    data = Path(path).read_bytes()
    if len(data) != ARCHIVE_BYTES or sha256(data) != ARCHIVE_SHA256:
        raise ValueError("NTL 1.5 archive does not match the authenticated compressed bytes")
    raw = subprocess.run(["gzip", "-dc"], input=data, capture_output=True,
                         check=True, timeout=30).stdout
    selected = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        for member in archive.getmembers():
            # Select bytes; do not use tarfile.extract or execute archived scripts.
            if member.name in MEMBERS:
                if not member.isfile() or member.name in selected:
                    raise ValueError("Unexpected or duplicate source archive member")
                selected[member.name] = archive.extractfile(member).read()
    if set(selected) != set(MEMBERS):
        raise ValueError("Required historical source member is absent")
    for name, expected in MEMBERS.items():
        if sha256(selected[name]) != expected:
            raise ValueError(f"Historical source hash mismatch: {name}")
    return selected


def model(seed, operation, argument, width):
    """Independent direct transcription of the recovered integer semantics."""
    state = None if seed is None else seed % M or 1
    consumed = 0

    def draw(bound):
        nonlocal state, consumed
        if bound <= 0:
            return 0
        if state is None:
            state = 7157891
        threshold = M - M % bound
        while True:
            state = A * state % M
            consumed += 1
            if state < threshold:
                return state % bound

    if operation == "draw":
        value = draw(argument)
    elif operation == "bnd":
        value = 0
        if argument > 1:
            count = (argument.bit_length()-1)//width+2
            for _ in range(count):
                value = value*(1 << width)+draw(1 << width)
            value %= argument
    elif operation == "len":
        value = 0 if argument <= 0 else 1
        if argument > 1:
            count = (argument+width-1)//width
            value = sum(draw(1 << width) << (i*width) for i in range(count))
            value &= (1 << (argument-1))-1
            value |= 1 << (argument-1)
    else:
        raise ValueError("Unknown historical operation")
    return {"value": value, "state": state, "raw_transitions": consumed}


def specifications(width):
    """Fixed coverage: arithmetic seeds, exact boundaries, wrappers, rejection."""
    cases = []
    seeds = (None, 0, 1, -1, M, -M, M+1, -(M+1), (1 << 200)+12345,
             -((1 << 200)+12345))
    for seed in seeds:
        for bound in (-1, 0, 1, 3, 1 << width):
            cases.append((seed, "draw", bound, "seed-and-scalar-boundaries"))
        for bound in (-1, 0, 1, 2, (1 << width)-1, 1 << width,
                      (1 << width)+1, (1 << (2*width))-1,
                      1 << (2*width), (1 << (2*width))+1, (1 << 521)-1):
            cases.append((seed, "bnd", bound, "bounded-assembly-and-limb-count"))
        for length in (-1, 0, 1, 2, width-1, width, width+1,
                       2*width-1, 2*width, 2*width+1, 520, 521):
            cases.append((seed, "len", length, "exact-length-mask-and-consumption"))
    # Force the next transition exactly to the acceptance boundary, then one
    # below it. The equality case must be rejected (source comparison >=).
    threshold = M-M % (1 << width)
    for emitted in (threshold-1, threshold, M-1):
        seed = pow(A, -1, M)*emitted % M
        for operation, argument in (("draw", 1 << width),
                                    ("bnd", (1 << 521)-1), ("len", 521)):
            cases.append((seed, operation, argument, "forced-rejection-threshold"))
    return cases


def decode_limbs(rep, width, nullable=False):
    if rep is None and nullable:
        return None
    if (not isinstance(rep, list) or not rep or type(rep[0]) is not int
            or len(rep) != abs(rep[0])+1
            or any(type(v) is not int or not 0 <= v < 1 << width for v in rep[1:])):
        raise ValueError("Invalid historical integer representation")
    value = sum(v << (i*width) for i, v in enumerate(rep[1:]))
    return -value if rep[0] < 0 else value


def replay_archive(path, compiler="gcc"):
    members = authenticate_archive(path)
    if not shutil.which(compiler):
        raise ValueError(f"C compiler not found: {compiler}")
    compiler_version = subprocess.run([compiler, "--version"], capture_output=True,
                                      text=True, check=True, timeout=10).stdout.splitlines()[0]
    builds = []
    with tempfile.TemporaryDirectory(prefix="perfectjet-ntl15-") as folder:
        root = Path(folder)
        for name, content in members.items():
            (root/name).write_bytes(content)
        (root/"replay.c").write_text(DRIVER)
        subprocess.run([compiler, *FLAGS, "MakeDesc.c", "MakeDescAux.c", "-o", "MakeDesc"],
                       cwd=root, capture_output=True, check=True, timeout=60)
        subprocess.run([str(root/"MakeDesc")], cwd=root, capture_output=True, check=True, timeout=10)
        original_config = (root/"mach_desc.h").read_text()
        if sha256(original_config.encode()) != NATIVE_CONFIG_SHA256:
            raise ValueError("Source-generated native machine description differs from the pinned replay configuration")
        descriptors = {name: int(re.search(r"#define "+name+r" \((-?\d+)\)", original_config)[1])
                       for name in ("ZZ_BITS_PER_LONG", "ZZ_DOUBLE_PRECISION", "ZZ_NBITS", "ZZ_SINGLE_MUL_OK")}
        if descriptors != {"ZZ_BITS_PER_LONG": 64, "ZZ_DOUBLE_PRECISION": 53,
                           "ZZ_NBITS": 50, "ZZ_SINGLE_MUL_OK": 0}:
            raise ValueError("Replay currently requires the source-generated 64-bit/IEEE53 configuration without SINGLE_MUL")
        for width in WIDTHS:
            # Only the radix descriptor is changed for the explicitly labeled
            # width26/30 emulations; no original C source expression is changed.
            config = re.sub(r"(#define ZZ_NBITS) \(\d+\)", rf"\g<1> ({width})", original_config)
            (root/"mach_desc.h").write_text(config)
            subprocess.run([compiler, *FLAGS, "replay.c", "IsFinite.c", "-lm", "-o", "replay"],
                           cwd=root, capture_output=True, check=True, timeout=60)
            observations = []
            for seed, operation, argument, category in specifications(width):
                stdout = subprocess.run([str(root/"replay"), operation,
                                         "*" if seed is None else str(seed), str(argument)],
                                        cwd=root, capture_output=True, text=True,
                                        check=True, timeout=10).stdout
                output = json.loads(stdout)
                if output["width"] != width:
                    raise ValueError("Compiled radix differs from requested replay")
                actual = {"value": decode_limbs(output["value"], width),
                          "state": decode_limbs(output["state"], width, nullable=True)}
                expected = model(seed, operation, argument, width)
                if any(actual[k] != expected[k] for k in actual):
                    raise ArithmeticError(f"Historical C replay mismatch at {(width, seed, operation, argument)}")
                observations.append({"seed": seed, "operation": operation, "argument": argument,
                                     "category": category, **actual,
                                     "model_raw_transitions": expected["raw_transitions"]})
            builds.append({"width": width,
                           "configuration": "native-generated" if width == 50 else "radix-emulation-on-64-bit-host; not-native-32-bit-or-SINGLE_MUL",
                           "mach_desc": config, "mach_desc_sha256": sha256(config.encode()),
                           "observations": observations})
    return {"schema": "perfectjet/ntl15-source-replay/1", "archive_url": ARCHIVE_URL,
            "archive_sha256": ARCHIVE_SHA256, "archive_bytes": ARCHIVE_BYTES,
            "source_members_sha256": MEMBERS, "driver_sha256": sha256(DRIVER.encode()),
            "compiler": compiler_version, "compiler_flags": FLAGS,
            "original_machine_descriptors": descriptors, "builds": builds,
            "case_count": sum(len(b["observations"]) for b in builds),
            "all_observations_agree": True,
            "scope": "Empirical replay of fixed semantic controls against authenticated NTL1.5 C source; not an all-state proof, not NTL2/3 evidence, not a P-521 origin reconstruction."}


def verify_document(document):
    """Validate fixed coverage and model consistency of retained C observations.

    This cannot authenticate the execution event; rerun --archive for that.
    """
    try:
        if (document["schema"] != "perfectjet/ntl15-source-replay/1"
                or document["archive_url"] != ARCHIVE_URL
                or document["archive_sha256"] != ARCHIVE_SHA256
                or document["archive_bytes"] != ARCHIVE_BYTES
                or document["source_members_sha256"] != MEMBERS
                or document["driver_sha256"] != sha256(DRIVER.encode())
                or document["compiler_flags"] != FLAGS
                or document["all_observations_agree"] is not True
                or len(document["builds"]) != len(WIDTHS)
                or document["original_machine_descriptors"] != {
                    "ZZ_BITS_PER_LONG": 64, "ZZ_DOUBLE_PRECISION": 53,
                    "ZZ_NBITS": 50, "ZZ_SINGLE_MUL_OK": 0}):
            return False
        count = 0
        native_config = document["builds"][-1]["mach_desc"]
        if sha256(native_config.encode()) != NATIVE_CONFIG_SHA256:
            return False
        for build, width in zip(document["builds"], WIDTHS):
            config = build["mach_desc"]
            expected_config = re.sub(r"(#define ZZ_NBITS) \(\d+\)",
                                     rf"\g<1> ({width})", native_config)
            if (build["width"] != width or build["mach_desc_sha256"] != sha256(config.encode())
                    or config != expected_config
                    or re.search(r"#define ZZ_NBITS \("+str(width)+r"\)", config) is None
                    or len(build["observations"]) != len(specifications(width))):
                return False
            for name, value in document["original_machine_descriptors"].items():
                if name != "ZZ_NBITS" and f"#define {name} ({value})" not in config:
                    return False
            label = "native-generated" if width == 50 else "radix-emulation-on-64-bit-host; not-native-32-bit-or-SINGLE_MUL"
            if build["configuration"] != label:
                return False
            for record, spec in zip(build["observations"], specifications(width)):
                seed, operation, argument, category = spec
                if tuple(record[k] for k in ("seed", "operation", "argument", "category")) != spec:
                    return False
                expected = model(seed, operation, argument, width)
                if (record["value"] != expected["value"] or record["state"] != expected["state"]
                        or record["model_raw_transitions"] != expected["raw_transitions"]):
                    return False
                count += 1
        return document["case_count"] == count
    except (KeyError, TypeError, ValueError, OverflowError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--archive", type=Path, help="execute the exact authenticated .tar.Z source")
    action.add_argument("--verify", type=Path, help="check recorded observations offline; does not reexecute C")
    parser.add_argument("--compiler", default=os.environ.get("CC", "gcc"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results")/"ntl15-source-replay.json")
    args = parser.parse_args()
    if args.verify:
        valid = verify_document(json.loads(args.verify.read_text()))
        print(json.dumps({"valid": valid, "mode": "retained-observation-consistency-only"}))
        return 0 if valid else 1
    document = replay_archive(args.archive, args.compiler)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"case_count": document["case_count"], "all_observations_agree": True,
                      "widths": list(WIDTHS), "archive_sha256": ARCHIVE_SHA256}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
