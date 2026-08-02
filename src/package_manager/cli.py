import sys
import argparse
from .config import Config
from .installer import install_all, list_installed
from .resolver import resolve_dependencies

def main():
    parser = argparse.ArgumentParser(prog="boubel", description="Bou.Bel Package Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    
    # install
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("packages", nargs="*", help="Packages to install (if omitted, install all from boubel.toml)")

    # list
    list_parser = subparsers.add_parser("list", help="List installed packages")

    args = parser.parse_args()

    if args.command == "init":
        config = Config.create_default()
        print("✅ Created boubel.toml")
    elif args.command == "install":
        if args.packages:
            print(f"Installing specified packages: {args.packages}")
            # Implémenter l'installation de paquets spécifiques
        else:
            install_all()
    elif args.command == "list":
        list_installed()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()