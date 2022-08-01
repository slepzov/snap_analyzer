import tarfile
import sys

file_name = sys.argv[1]

if __name__ == "__main__":
    with tarfile.open(file_name) as tar:
        tar.extractall(path=file_name[:-4])

