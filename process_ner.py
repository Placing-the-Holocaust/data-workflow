import glob
import datasets
import pandas as pd
import spacy
from src.data.ner import process_files
from src.data.clean import clean_ner_header
from src.nlp.pipeline import GeoPipeline

metadata = datasets.load_dataset("placingholocaust/testimony-metadata")["train"]
testimonies_metadata = pd.DataFrame(metadata)

# labels = ["dlf", "populated place", "country", "region", "interior space", "env feature", "building", "spatial object"]

# gliner_config = {"gliner_model": "placingholocaust/gliner_small-v2.1-holocaust",
#                  "labels": labels,
#                  "chunk_size": 300,
#                  "map_location": "cuda"}

# pipeline  = GeoPipeline(gliner_config)

pipeline  = GeoPipeline()

# nlp = spacy.blank("en")
# nlp.add_pipe("gliner_spacy", config=gliner_config)



html_input_directory = "./data/05_final_removals/"
ner_output_directory = "./data/04_html_ner_2/"

# Usage example:
process_files(html_input_directory, ner_output_directory, pipeline, testimonies_metadata)

clean_ner_output_directory = "./data/07_ner_cleaned/"
# Clean NER headers for all files in the output directory
clean_ner_header(ner_output_directory, clean_ner_output_directory)
