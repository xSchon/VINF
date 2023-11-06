import csv
import lucene

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import MMapDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from java.nio.file import Paths

lucene.initVM()
INDEX_DIR = 'players_index'

def create_index():
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    index = MMapDirectory(Paths.get(INDEX_DIR))  
    writer = IndexWriter(index, config)

    processed = 0
    with open('data/players.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')

        # Skip the header line if needed
        next(csv_reader, None)

        for row in csv_reader:
            doc = Document()	
            doc.add(Field('PlayerName', row[0], TextField.TYPE_STORED))
            doc.add(Field('TeamHistory', row[1], TextField.TYPE_STORED))
            doc.add(Field('HistoryText', row[2], TextField.TYPE_STORED))
            doc.add(Field('PlayerCard', row[3], TextField.TYPE_STORED))
            doc.add(Field('TournamentResults', row[4], TextField.TYPE_STORED))
            doc.add(Field('ChampionsStats', row[5], TextField.TYPE_STORED))        
            writer.addDocument(doc)

            processed += 1
            if processed > 1000: 
                break
        f.close()

    writer.commit()
    writer.close()
    return(analyzer, index)


def search_query(analyzer, index, to_check='Korea', where_check = "PlayerCard", results_amount = 5):
    query_parser = QueryParser(where_check, analyzer)
    index_reader = DirectoryReader.open(index)
    searcher = IndexSearcher(index_reader)

    search_query = query_parser.parse(to_check)
    query_results = searcher.search(search_query, results_amount)  

    x = 0
    print(f"Total amount of results {len(query_results.scoreDocs)}")
    for res in query_results.scoreDocs:
        x += 1
        print(f"Result number {x}")

        doc = searcher.doc(res.doc)
        PlayerName = doc.get("PlayerName")

        print(f"PlayerName: {PlayerName}")
        print(f"Data found {doc.get(where_check)}")
        print("******************************************\n\n")
        
    # Close the index reader
    index_reader.close()


ana, idx = create_index()
search_query(ana, idx, 'EU')