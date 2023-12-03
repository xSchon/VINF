import csv
import os
import lucene

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import FSDirectory
from java.nio.file import Paths

# Change paths accordingly
FILE_PATH = os.getcwd()
INDEX_DIR = f"{FILE_PATH}/players_index"
CSV_FILE = f"{FILE_PATH}/data/final_data.csv"
lucene.initVM()


def create_index(index_dir: str, csv_file_path: str) -> None:
    """
    Function for index creation for all of the rows in the csv file.
    args:
        str: index_dir - where to save the index (dirname)
        str: csv_file_path - csv file to index
    """
    # Initialize lucene indexer
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    writer = IndexWriter(FSDirectory.open(Paths.get(index_dir)), config)

    with open(csv_file_path, "r") as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter="\t")

        for row in csv_reader:
            document = Document()

            for field_name, field_value in row.items():
                document.add(TextField(field_name, field_value, Field.Store.YES))

            # Add index to document
            writer.addDocument(document)

    writer.close()


create_index(INDEX_DIR, CSV_FILE)
