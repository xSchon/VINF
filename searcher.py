import lucene
import os

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import BooleanClause, BooleanQuery
from org.apache.lucene.queryparser.classic import MultiFieldQueryParser, QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import FSDirectory
from java.nio.file import Paths

lucene.initVM()
# Change paths accordingly, as needed
FILE_PATH = os.getcwd()
INDEX_DIR = f"{FILE_PATH}/players_index"


class Searcher:
    """Create class for searching in index created over players, in indexer.py"""

    def __init__(self, index_dir=INDEX_DIR) -> None:
        self.index_dir = index_dir

    def search_index(
        self,
        fields_to_search: list,
        queries: list,
        printable_cols: list = ["Team", "PlayerName"],
        results_amount: str = "5",
        search_type: str = "OR",
    ) -> list:
        """
        Main searching class
        args:
            :list fields_to_search - which columns to search in
            :list queries - representing words to search in columns on same positions in fields_to_search
            :list printable_cols - data from which columns to show to the end user
            :str results_amount - how many results to show. Default 5, can be int in string, or 'All' for all results
            :str search_type - how to access different columns and searches. Deafult OR, can be OR or AND

        returns:
            list containing prepared strings of information filtered accordingly to the query
        """

        # Create an IndexSearcher
        directory = FSDirectory.open(Paths.get(self.index_dir))
        reader = DirectoryReader.open(directory)
        searcher = IndexSearcher(reader)

        # Build a query over multiple columns
        boolean_query = BooleanQuery.Builder()
        for field, query_text in zip(fields_to_search, queries):
            query_parser = QueryParser(field, StandardAnalyzer())
            field_query = query_parser.parse(query_text)
            # OR query
            if search_type == "OR":
                boolean_query.add(field_query, BooleanClause.Occur.SHOULD)
            # AND query
            else:
                boolean_query.add(field_query, BooleanClause.Occur.MUST)

        # Filter
        final_query = boolean_query.build()
        top_docs = searcher.search(final_query, reader.maxDoc())

        # Print the total number of results found from the dataset
        total_results = top_docs.totalHits
        print(f"Total results: {total_results}")

        # Iterate through all results and prepare string selecting fitting
        results = []
        if results_amount == "All":
            results_amount = reader.maxDoc()  # maximum results
        results_amount = int(results_amount)

        for score_doc in sorted(
            top_docs.scoreDocs, key=lambda x: x.score, reverse=True
        ):
            doc_id = score_doc.doc
            relevance_score = score_doc.score

            document = searcher.doc(doc_id)
            printable_string = ""
            for toprint in printable_cols:
                printable_string += f"{toprint}: {document.get(toprint)}  "

            # Select unique
            if printable_string not in results:
                results.append(printable_string)
                results_amount -= 1

            if results_amount <= 0:
                break

        return results
