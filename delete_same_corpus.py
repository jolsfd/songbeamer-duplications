import similar
import zlib
import sys
import os
from typing import List

def compare_songs(
    path_0: str, potential_duplicates: List[str], duplicates_to_delete: List[str]
):
    corpus_0 = similar.read_song_corpus_normalized(path_0)
    num_metadata_lines_0 = similar.count_metadata_lines(path_0)

    for i in range(len(potential_duplicates)):
        corpus_1 = similar.read_song_corpus_normalized(potential_duplicates[i])

        if corpus_0 != corpus_1:
            print("checksum collision detected")
            continue

        # if identical corpus compare metadata
        num_metadata_lines_1 = similar.count_metadata_lines(potential_duplicates[i])

        if num_metadata_lines_0 > num_metadata_lines_1:
            # swap paths in cache
            temp = potential_duplicates[i]

            potential_duplicates[i] = path_0

            path_0 = temp

        # debug
        # print(potential_duplicates[i])
        # print(path_0)

        duplicates_to_delete.append(path_0)
        return


def main(root_dir, backup_dir):
    paths = similar.collect_songs(root_dir)

    cache = {}
    duplicates_to_delete = []

    for path in paths:
        corpus_normalized = similar.read_song_corpus_normalized(path)
        corpus_normalized_bytes = bytes(corpus_normalized, "ISO-8859-1")

        checksum = zlib.adler32(corpus_normalized_bytes)

        # debugging
        # print(f"path: {path}")
        # print(f"checksum: {checksum}")

        try:
            cache[checksum]
        except KeyError:
            # new entry in cache
            cache[checksum] = [path]
            continue

        compare_songs(path, cache[checksum], duplicates_to_delete)

    print(f"moving {len(duplicates_to_delete)} songs to backup directory")

    for path in duplicates_to_delete:
        similar.delete_song(path, backup_dir)


if __name__ == "__main__":
    BACKUP_DIR = os.path.join(os.getcwd(), "backup")

    # ensure the backup folder exists
    if not os.path.isdir(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    print("=== Remove songs with identical corpus ===")

    root_dir = sys.argv[1]

    print(f"root_dir: {root_dir}")
    print(f"backup_dir: {BACKUP_DIR}")

    main(root_dir, BACKUP_DIR)