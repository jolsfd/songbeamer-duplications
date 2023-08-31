# songbeamer-duplications

This is a small utitlity that helps to organize your songbeamer song archive. This app detects similar or almost identical songs by training a doc2vec model.
It also provides a graphical interface to delete/remove songs that are identical from your archive. Please note that this gui isn't designed to be beautiful and provides you only with a barebone functionality.

## quick start

1. install python on your system 🐍
2. (optional) create a virtual environment 
```bash
python -m venv venv
```

3. install all requirements 
```bash
pip install -r requirements.txt
```

4. train the doc2vec model
```bash
$ python train.py --help
usage: Train doc2vec model from songbeamer files [-h] [--output_file OUTPUT_FILE] [--vector_size VECTOR_SIZE] [--epochs EPOCHS]
                                                 [--pick_probability PICK_PROBABILITY]
                                                 training_dir

positional arguments:
  training_dir          directory where the training data lives

options:
  -h, --help            show this help message and exit
  --output_file OUTPUT_FILE
                        directory where the trained model lives
  --vector_size VECTOR_SIZE
  --epochs EPOCHS
  --pick_probability PICK_PROBABILITY
```


4. find similar songs
```bash
$ python find.py --help
usage: Find similar songs from in a directory [-h] [--model_file MODEL_FILE] [--output_file OUTPUT_FILE] [--min MIN] dir

positional arguments:
  dir                   directory where the songs lives

options:
  -h, --help            show this help message and exit
  --model_file MODEL_FILE
                        file where the model is stored
  --output_file OUTPUT_FILE
                        file where all duplicate songs are stored in json format
  --min MIN             minimum similarity to be found in percent
```

5. start the gui
```bash
$ python gui.py --help
usage: GUI for better accessibility [-h] [--data_file DATA_FILE]

options:
  -h, --help            show this help message and exit
  --data_file DATA_FILE
                        directory where the trained model lives
```

## tipps and tricks

* No songs are going to be deleted! Instead they will be safed in a backup directory, that is located in the working directory where you started the program.
* The best model was established by using 60-70 Epochs, 300 Vector size and pick percentage of 3,5% for a big archive.
* Don't move the folder with the song archive after finding the duplicate songs because it uses full paths instead of relative paths. This is caused by a much easier program logic.
* be happy 🥳

## credits
* [gensim](https://radimrehurek.com/gensim/) ❤️