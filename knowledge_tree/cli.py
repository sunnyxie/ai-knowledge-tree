"""Simple CLI for knowledge-tree"""
import argparse
import json
import os
import sys
from .scanner import scan_root


def main(argv=None):
    parser = argparse.ArgumentParser(prog="knowledge-tree")
    sub = parser.add_subparsers(dest="cmd")

    scan = sub.add_parser("scan", help="Scan a root folder for projects")
    scan.add_argument("root", help="Root folder to scan")
    scan.add_argument("--output", choices=["json"], default="json", help="output format")

    args = parser.parse_args(argv)
    if args.cmd == "scan":
        result = scan_root(args.root)
        if args.output == "json":
            print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
