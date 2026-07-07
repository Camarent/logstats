from pathlib import Path


def file_len(filename: Path) -> int:
    with filename.open("rb") as f:
        num_lines = sum(1 for _ in f)
        return num_lines


def main():
    filename = Path("README.md")
    line_count = file_len(filename)
    print("File line count is", line_count)


if __name__ == "__main__":
    main()
