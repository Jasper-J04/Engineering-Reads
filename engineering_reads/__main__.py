import argparse
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

from .contract import ContractError, validate


def main():
    parser = argparse.ArgumentParser(description="Validate content or build Engineering Reads")
    parser.add_argument("command", choices=["validate", "build"])
    parser.add_argument("--demo", action="store_true", help="use the isolated sample articles")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data_root = root / "demo" if args.demo else root
    try:
        count = validate(data_root, root / "topics.json")
        print(f"Validated {count} articles.", flush=True)
        if args.command == "build":
            branch = os.getenv("CF_PAGES_BRANCH")
            if args.demo and branch:
                raise ContractError("Cloudflare Pages builds use the production content set")
            if branch == "main":
                site = urlsplit(os.getenv("SITE_URL", ""))
                if (site.scheme != "https" or not site.hostname or site.path not in ("", "/")
                        or site.query or site.fragment or site.username):
                    raise ContractError("Cloudflare production SITE_URL must be the public HTTPS site origin")
            result = subprocess.run(
                [sys.executable, "-m", "pelican", "--settings", "pelicanconf.py",
                 "--fatal", "errors", "--delete-output-directory"],
                cwd=root,
                env={**os.environ, "ENGINEERING_READS_DEMO": "1" if args.demo else "0"},
            )
            return result.returncode
    except (OSError, ValueError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
