import gensim
import os
import random
import numpy as np
import multiprocessing as mp
import pickle
import json
from typing import List
from scipy.spatial import distance


class Song:
    def __init__(self, path, vector) -> None:
        self.path = path
        self.vector = vector


def is_separator(line, chars="---"):
    """Checks if a line is a seperator

    Args:
        line: The text to check.

    Returns:
        A Boolean saying if it is a seperator or not.
    """
    if len(line) >= len(chars):
        if line[: len(chars)] == chars:
            return True

    return False


def read_song_corpus(filename: str, reading_chars="---") -> str:
    with open(filename, "r", encoding="ISO-8859-1") as f:
        output = ""
        reading = False

        for line in f:
            if reading and not is_separator(line):
                # output += line.rstrip("\n") + " "  # only right rstrip("\n")
                output += line
                continue

            if line[: len(reading_chars)] == reading_chars:
                reading = True

    return output
    # return gensim.utils.simple_preprocess(output)


def read_song_corpus_normalized(filename: str) -> str:
    return read_song_corpus(filename).replace(" ", "")


def read_song_corpus_tokens(filename: str) -> List[str]:
    raw_corpus = read_song_corpus(filename)
    raw_corpus.replace("\n", " ")
    raw_corpus.replace("-", "")

    return gensim.utils.simple_preprocess(raw_corpus)


def count_metadata_lines(filename: str, reading_chars="---") -> int:
    lines_count = 0

    with open(filename, "r", encoding="ISO-8859-1") as f:
        for line in f:
            if line == reading_chars:
                break

            lines_count += 1

    return lines_count


def collect_training_data(
    root: str, n_pick=0.035, extension=".sng"
) -> List[gensim.models.doc2vec.TaggedDocument]:
    train_corpus = []

    for root_dir, dirs, files in os.walk(root):
        # pick a certain amounts of files random for training data
        for filename in random.sample(files, int(len(files) * n_pick)):
            _, file_extension = os.path.splitext(filename)

            if file_extension != extension:
                continue

            path = os.path.join(root_dir, filename)

            tokens = read_song_corpus_tokens(path)

            train_corpus.append(
                gensim.models.doc2vec.TaggedDocument(tokens, [filename])
            )

    return train_corpus


def train_model(
    train_corpus: List[gensim.models.doc2vec.TaggedDocument], vector_size=100, epochs=40
):
    model = gensim.models.doc2vec.Doc2Vec(
        vector_size=vector_size, min_count=2, epochs=epochs
    )

    model.build_vocab(train_corpus)
    # print(f"Word 'jesus' appeared {model.wv.get_vecattr('jesus', 'count')} times in the training corpus.")
    # print(f"Word 'gott' appeared {model.wv.get_vecattr('gott', 'count')} times in the training corpus.")

    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)

    return model


def compute_similarity(vectors: np.ndarray):
    distance_matrix = distance.cdist(vectors, vectors, "cosine")

    # replace 0 with nan
    # distance_matrix[np.isclose(distance_matrix, 0)] = np.nan # maybe ignoring erst später damit zu 100% alle lieder abgegriffen werden

    return distance_matrix


def collect_songs(root: str, extension=".sng"):
    paths = []

    for root_dir, dirs, files in os.walk(root):
        for filename in files:
            _, file_extension = os.path.splitext(filename)

            if file_extension != extension:
                continue

            path = os.path.join(root_dir, filename)

            paths.append(path)

    return paths


def read_songs(paths):
    with mp.Pool(processes=4) as pool:
        # Read the content of each file
        contents = pool.map(read_song_corpus_tokens, paths)

    return contents


def build_vectors(model, paths, contents):
    songs = {}
    vectors = np.empty([len(paths), model.vector_size])

    for i, path in enumerate(paths):
        vector = model.infer_vector(contents[i])
        vectors[i] = vector

        songs[i] = Song(path, vector)

    return songs, vectors


def build_vectors_pool(model, paths, contents, processes=4, chunksize=30):
    songs = {}
    vectors = np.empty([len(paths), model.vector_size])

    with mp.Pool(processes) as pool:
        computed_vectors = pool.map(model.infer_vector, contents, chunksize)

        for i in range(len(computed_vectors)):
            vectors[i] = computed_vectors[i]

            songs[i] = Song(paths[i], computed_vectors[i])

    return songs, vectors


def save_model(model, filename: str):
    with open(filename, "wb") as f:
        pickle.dump(model, f)


def load_model(filename: str):
    with open(filename, "rb") as f:
        model = pickle.load(f)

    return model


def display_similar_songs(pairs):
    counter = 0
    for pair in pairs:
        counter += len(pair) - 1
        [print("[" + os.path.basename(song_path) + "]", end=" ") for song_path in pair]
        print()

    print(counter, "possible duplicates")


def find_similar_songs(distance_matrix, songs_dict, probability=0.95):
    min_distance = 2 - 2 * probability
    duplicates = []
    cache_already_found = {}

    for i in range(len(distance_matrix)):
        pair = []

        similar_songs = np.where((distance_matrix[i] <= min_distance))[0]

        # filter songs
        for song_i in similar_songs:
            try:
                cache_already_found[song_i]
            except KeyError:
                cache_already_found[song_i] = 1
                pair.append(songs_dict[song_i].path)

        # no similar song has been found
        if len(pair) <= 1:
            continue

        duplicates.append(pair)

    return duplicates


def save_duplicates(filename: str, data):
    json_object = json.dumps(data, indent=2)

    with open(filename, "w") as f:
        f.write(json_object)

    return


def read_duplicates(filename: str, create_file=True):
    if create_file:
        # ensure the file exists
        if not os.path.isfile(filename):
            with open(filename, "w") as f:
                f.write(json.dumps([[]]))

    with open(filename, "r") as f:
        duplicates = json.load(f)

    return duplicates

def delete_song(path: str, backup_dir: str):
    counter = 0
    basename = os.path.basename(path)
    new_path = os.path.join(backup_dir, basename)

    while True:
        if os.path.exists(new_path):
            counter += 1
            new_path = os.path.join(
                backup_dir,
                os.path.splitext(basename)[0]
                + str(counter)
                + os.path.splitext(basename)[1],
            )
            continue

        break

    try:
        os.rename(path, new_path)

    except:
        print(f"an error occured while moving {path}")
        return


# if __name__ == "__main__":
#     model = load_model("./riesig.bin")

#     print("Collecting song files...")
#     paths = collect_songs("./Songs")

#     print("Reading song files...")
#     contents = read_songs(paths)

#     print("Computing vectors...")
#     songs, vectors = build_vectors(model, paths, contents)

#     print("Computing similarity...")
#     distance_matrix = compute_similarity(vectors)

#     # print(distance_matrix)

#     print("Displaying similar files...")
#     pairs = find_similar_songs(distance_matrix, songs)

#     print("Saving duplicates to json...")
#     save_duplicates("out.json", pairs)

#     display_similar_songs(pairs)
