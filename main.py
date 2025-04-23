import argparse
import os
import json
from collection import Collection
from tag import TagType

ROOT = ".yaac"
ACTIVE_FILE = os.path.join(ROOT, "HEAD")
MANIFEST_FILE = os.path.join(ROOT, "MANIFEST")


def get_active_collection_path():
    if not os.path.exists(ACTIVE_FILE):
        print("No active collection. Use 'yaac use <label>' to activate one.")
        exit(1)
    with open(ACTIVE_FILE, "r") as f:
        return f.read().strip()


def load_active_collection():
    path = get_active_collection_path()
    ulid = os.path.basename(path).split(".")[0]
    col = Collection("temp")
    col.ulid = ulid
    col.read()
    return col

def get_partition_path(ulid):
    return os.path.join(ROOT, ulid[:2], ulid[2:4], f"{ulid}.json")

def find_collection_by_label(label):
    with open(MANIFEST_FILE, "r") as mf:
        for line in mf:
            col_label, col_ulid = line.strip().split("=")
            if col_label == label or col_ulid == label:
                collection_path = get_partition_path(col_ulid)
                if os.path.exists(collection_path):
                    with open(collection_path, "r") as j:
                        data = json.load(j)
                        return data, collection_path
    return None, None

def cmd_init(args):
    if os.path.exists(ROOT):
        print(f"{ROOT} already exists. No need to initialize.")
        return

    os.makedirs(ROOT)

    with open(ACTIVE_FILE, "w") as f:
        f.write("")

    with open(MANIFEST_FILE, "w") as f:
        f.write("")
    print(f"Initialized {ROOT} directory with {ACTIVE_FILE} and {MANIFEST_FILE}.")


def cmd_collection(args):
    if args.action == "add":
        col = Collection(args.label)
        col.write()
        with open(MANIFEST_FILE, "a") as mf:
            mf.write(f"{col.label}={col.ulid}\n")
        print(f"Collection created: {col.label} ({col.ulid})")

    elif args.action == "list":
        with open(MANIFEST_FILE, "r") as mf:
            for line in mf:
                col_label, col_ulid = line.strip().split("=")
                print(f"{col_ulid}\t{col_label}")

    elif args.action == "rm":
        collection_found = False
        with open(MANIFEST_FILE, "r") as mf:
            lines = mf.readlines()
        with open(MANIFEST_FILE, "w") as mf:
            for line in lines:
                col_label, col_ulid = line.strip().split("=")
                if col_label == args.label:
                    collection_found = True
                    collection_file = get_partition_path(col_ulid)
                    confirm = input(
                        f"Confirm delete of {args.label} ({col_ulid}) (y/N): "
                    )
                    if confirm.lower() == "y":
                        if os.path.exists(collection_file):
                            os.remove(collection_file)
                            print(f"Deleted collection file: {collection_file}")
                        else:
                            print(f"Collection file {collection_file} not found.")
                    continue
                mf.write(line)

        if not collection_found:
            print(f"Collection {args.label} not found.")
        else:
            print("Collection deleted successfully.")

    elif args.action == "show":
        data, _ = find_collection_by_label(args.label)
        if data:
            print(json.dumps(data, indent=2))
        else:
            print("Collection not found.")

def cmd_card(args):
    pass

def cmd_use(args):
    data, full = find_collection_by_label(args.label)
    if full:
        with open(ACTIVE_FILE, "w") as af:
            af.write(full)
        print(f"Now using collection: {data['label']}")
    else:
        print("Collection not found.")


def cmd_which(args):
    path = get_active_collection_path()
    with open(path, "r") as f:
        data = json.load(f)
        print(f"Active collection: {data['label']} ({data['ulid']})")


def main():
    parser = argparse.ArgumentParser(
        prog="yaac",
        description="Yet Another Anki Clone",
        epilog="""
        Commands:
        init                         Create the .yaac environment
        collection add <label>       Add a new collection
        collection list              List all collections
        collection show <label|ulid> Show details of a collection
        collection rm <label|ulid>   Remove a collection

        use <label>                  Set the active collection
        which                        Show the active collection

        card add <front> <back>     Add a flashcard
        card list                   List all flashcards
        card show <label|ulid>      Show details of a card
        card assign <label|ulid>    Assign card to a deck
        card rm <label|ulid>        Remove a card

        tag add <name> [type]       Add a tag with optional type (default: Generic)
        tag list                    List all tags
        tag show <label|ulid>       Show details of a tab
        tag assign <label|ulid>     Assign tag to a card
        tag rm <label|ulid>        Remove a tag

        deck add <name>             Add a new deck
        deck list                   List all decks
        deck show <label|ulid>            Show deck details
        deck rm <label|ulid>              Remove a deck

        review start                Start a review session
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize the .yaac environment",
        description="Create the .yaac directory along with HEAD and MANIFEST files",
    )
    init_parser.set_defaults(func=cmd_init)

    # collection
    collection_parser = subparsers.add_parser("collection")
    collection_parser.add_argument("action", choices=["add", "list", "show", "rm"])
    collection_parser.add_argument(
        "label", nargs="?", help="Label of the collection (required for add, show, rm)"
    )
    collection_parser.set_defaults(func=cmd_collection)

    # use
    use_parser = subparsers.add_parser("use")
    use_parser.add_argument("label")
    use_parser.set_defaults(func=cmd_use)

    # which
    which_parser = subparsers.add_parser("which")
    which_parser.set_defaults(func=cmd_which)

    # card
    card_parser = subparsers.add_parser("card")
    card_parser.set_defaults(func=cmd_card)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
