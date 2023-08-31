import similar
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Find similar songs from in a directory", description=""
    )

    parser.add_argument(
        "dir",
        type=str,
        default=os.getcwd(),
        help="directory where the songs lives",
    )

    parser.add_argument(
        "--model_file",
        type=str,
        default="songbeamer_model.bin",
        help="file where the model is stored",
    )

    parser.add_argument(
        "--output_file",
        type=str,
        default="similar_songs.json",
        help="file where all duplicate songs are stored in json format",
    )

    parser.add_argument(
        "--min",
        type=float,
        default=0.95,
        help="minimum similarity to be found in percent",
    )

    args = parser.parse_args()

    # load model
    model = similar.load_model(args.model_file)

    print("Collecting song files...")
    paths = similar.collect_songs(args.dir)

    print("Reading song files...")
    contents = similar.read_songs(paths)

    print("Computing vectors...")
    songs, vectors = similar.build_vectors(model, paths, contents)

    print("Computing similarity...")
    distance_matrix = similar.compute_similarity(vectors)

    #print(distance_matrix)

    print("Displaying similar files...")
    pairs = similar.find_similar_songs(distance_matrix, songs, probability=args.min)

    print("Saving duplicates to json...")
    similar.save_duplicates(args.output_file, pairs)

    similar.display_similar_songs(pairs)
