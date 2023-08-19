import argparse
import duplications
import logging
import os


if __name__ == "__main__":
    # gensim config
    logging.basicConfig(
        format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
    )

    parser = argparse.ArgumentParser(
        prog="Train doc2vec model from songbeamer files", description=""
    )

    parser.add_argument(
        "training_dir",
        type=str,
        default=os.getcwd(),
        help="directory where the training data lives",
    )

    parser.add_argument(
        "--output_file",
        type=str,
        default="songbeamer_model.bin",
        help="directory where the trained model lives",
    )

    parser.add_argument(
        "--vector_size",
        type=int,
        default=300,
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
    )

    parser.add_argument(
        "--pick_probability",
        type=float,
        default=1,
    )

    args = parser.parse_args()

    print("Collecting training data...")
    training_data = duplications.collect_training_data(
        args.training_dir, n_pick=args.pick_probability
    )
    print(len(training_data), "data files")

    print("Training model...")
    model = duplications.train_model(
        training_data, vector_size=args.vector_size, epochs=args.epochs
    )

    print("Saving model...")
    duplications.save_model(model, args.output_file)
