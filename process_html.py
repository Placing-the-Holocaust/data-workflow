import glob
from data.clean import clean_html
from data.sentences import add_sentences

# get approved files
html_files = glob.glob("./data/pdfs/*.html")
approved_files = []
for filename in html_files:
    if "sum" not in filename and "trs_en" in filename:
        approved_files.append(filename)

print(f"Processing {len(approved_files)} files!")


# output directories
clean_html_output_directory = "./data/cleaned_htmls/"
sentences_output_directory = './data/03_html_sentences/'
ner_output_directory = './data/04_html_ner/'
# clean htmls
for filename in approved_files:
    clean_html(filename, clean_html_output_directory)


# add sentences
add_sentences(clean_html_output_directory, sentences_output_directory)
