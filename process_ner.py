import glob
import datasets
import pandas as pd
import spacy
from src.data.ner import process_files
from src.data.clean import clean_ner_header

metadata = datasets.load_dataset("placingholocaust/testimony-metadata")["train"]
testimonies_metadata = pd.DataFrame(metadata)

labels = ["dlf", "populated place", "country", "region", "interior space", "env feature", "building", "spatial object"]

nlp = spacy.blank("en")
nlp.add_pipe("gliner_spacy", config={"gliner_model": "placingholocaust/gliner_small-v2.1-holocaust", "labels": labels, "chunk_size": 300, "map_location": "mps"})



html_input_directory = "./data/03_html_sentences/"
ner_output_directory = "./data/04_html_ner/"

# Usage example:
process_files(html_input_directory, ner_output_directory, nlp, testimonies_metadata)

clean_ner_output_directory = "/data/05_ner_cleaned/"
# Clean NER headers for all files in the output directory
clean_ner_header(ner_output_directory, clean_ner_output_directory)
