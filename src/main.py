import sys

from src.graph import run_workflow


def main() -> None:
    query = " ".join(sys.argv[1:]).strip() or "What is retrieval augmented generation?"
    print(run_workflow(query).report)


if __name__ == "__main__":
    main()

