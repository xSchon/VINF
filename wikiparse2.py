import re
import xml.etree.ElementTree as ET  

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

spark = SparkSession.builder \
    .appName("XMLtoJSON") \
    .config("spark.executor.memory", "16g") \
    .getOrCreate()

OUTPUT_FILE = '/data/'                                       # CHANGE ACCORDINGLY
PATH_TO_WIKIDUMP = 'data/enwiki-latest-pages-articles1.xml'  # CHANGE ACCORDINGLY
SAVE_TEAMS = OUTPUT_FILE+'/parsed_teams.json'
SAVE_COUNTRIES = OUTPUT_FILE+'/parsed_countries.json'

TEAMS_LIST_PATH = 'title_lists/teams_list.txt'  # CHANGE ACCORDINGLY
COUNTRIES_LIST_PATH = 'title_lists/countries_list.txt'  # CHANGE ACCORDINGLY

# Define a UDF to extract categories from content
@udf(StringType())
def extract_categories(content):
    category_pattern = re.compile(r'\[\[Category:(.*?)\]\]')
    categories = category_pattern.findall(content)
    return ','.join(categories)

xml_data = spark.read.text(PATH_TO_WIKIDUMP).rdd.map(lambda x: x[0])

@udf
def is_in_list(title, title_list):
    return title in title_list

# Read teams and countries list
teams_list = spark.read.text(TEAMS_LIST_PATH).rdd.map(lambda x: x[0]).collect()
countries_list = spark.read.text(COUNTRIES_LIST_PATH).rdd.map(lambda x: x[0]).collect()

# Process XML data
result_df = xml_data.flatMap(lambda line: line.split('</page>')) \
    .filter(lambda page: '<page>' in page) \
    .map(lambda page: ET.fromstring(page)) \
    .filter(lambda page: page.find(".//{http://www.mediawiki.org/xml/export-0.10/}title") is not None) \
    .map(lambda page: (
        page.find(".//{http://www.mediawiki.org/xml/export-0.10/}title").text.encode('utf-8'),
        page.find(".//{http://www.mediawiki.org/xml/export-0.10/}revision/{http://www.mediawiki.org/xml/export-0.10/}text").text.encode('utf-8') if page.find(".//{http://www.mediawiki.org/xml/export-0.10/}revision/{http://www.mediawiki.org/xml/export-0.10/}text") is not None else "No content"
    )) \
    .toDF(["title", "content"])

result_df = result_df.withColumn("categories", extract_categories(result_df["content"]))

# Filter teams and countries
teams_df = result_df.filter(is_in_list(result_df["title"], teams_list))
countries_df = result_df.filter(is_in_list(result_df["title"], countries_list))

# Save results as JSON
teams_df.write.json(SAVE_TEAMS)
countries_df.write.json(SAVE_COUNTRIES)

# Stop the Spark session
spark.stop()

