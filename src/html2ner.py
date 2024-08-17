import glob
import datasets
import pandas as pd
import spacy
from tqdm import tqdm
from bs4 import BeautifulSoup, Comment
import os
from pathlib import Path
import concurrent.futures
import multiprocessing

def create_yaml_header(row):
    # Function to create the YAML-like header from a dataframe row
    header = "---\n"
    header += f"layout: transcript\n"
    
    # Helper function to safely get values from the row
    def safe_get(column, default='none'):
        if column in row.index and pd.notna(row[column]):
            return str(row[column]).lower()
        return default

    header += f"interviewee: {safe_get('First Name')} {safe_get('Middle Name')} {safe_get('Last Name')}\n"
    header += f"rg_number: {safe_get('RG Number')}\n"
    header += f"pdf_url: {safe_get('PDF URL')}\n"
    header += f"ushmm_url: {safe_get('USHMM URL')}\n"
    header += f"gender: {safe_get('Gender')}\n"
    header += f"birth_date: {safe_get('Birth Date')}\n"
    header += f"birth_year: {safe_get('Birth Year')}\n"
    header += f"place_of_birth: {safe_get('Place of Birth')}\n"
    header += f"country: {safe_get('Country')}\n"
    header += f"experience_group: {safe_get('Experience Group')}\n"
    header += f"ghetto(s)_encyclopedia: {safe_get('Ghetto(s) Encyclopedia')}\n"
    header += f"ghetto: {safe_get('Ghetto')}\n"
    header += f"camp(s)_encyclopedia: {safe_get('Camp(s) Encyclopedia')}\n"
    header += f"camp: {safe_get('Camp')}\n"
    header += f"non_ss_camp: {safe_get('Non-SS Camp')}\n"
    header += f"region: {safe_get('Region')}\n"
    header += f"needs_research: {safe_get('Needs Research')}\n"
    header += f"data_entry: {safe_get('Data Entry')}\n"
    header += f"accession: {safe_get('Accession')}\n"
    header += f"revisit: {safe_get('Revisit')}\n"
    header += f"tags: transcripts\n"
    header += "---\n\n"
    return header

def process_html_with_spacy(html_content, nlp_model, yaml_header):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Add the YAML header as a comment at the top of the HTML
    header_comment = Comment(f"\n{yaml_header}\n")
    soup.insert(0, header_comment)
    
    # Find all sentence elements
    sentences = soup.find_all('sentence')
    
    for sentence in sentences:
        # Get the text content of the sentence
        text = sentence.get_text()
        
        # Process the text with spaCy
        doc = nlp_model(text)
        
        # Clear the sentence content
        sentence.clear()
        
        # Add annotated content
        last_end = 0
        for ent in doc.ents:
            # Add text before the entity
            sentence.append(text[last_end:ent.start_char])
            
            # Create a new span tag
            span_tag = soup.new_tag("span", attrs={"class": ent.label_})
            span_tag.string = text[ent.start_char:ent.end_char]
            sentence.append(span_tag)
            
            last_end = ent.end_char
        
        # Add any remaining text
        sentence.append(text[last_end:])
    
    # Return the modified HTML as a string
    return str(soup)

def process_single_file(args):
    input_path, output_path, nlp_model, testimonies_data = args
    filename = os.path.basename(input_path)
    
    # Check if output file already exists
    if os.path.exists(output_path):
        return f"Skipped {filename} (already exists)"
    
    # Extract the RG Number from the filename
    rg_number = filename.split('_')[0]
    
    # Find the corresponding row in testimonies_data
    testimony_row = testimonies_data[testimonies_data['RG Number'] == rg_number]
    
    if testimony_row.empty:
        return f"Skipped {filename} (no matching data found)"
    
    # Create the YAML header
    yaml_header = create_yaml_header(testimony_row.iloc[0])
    
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Process the HTML content
    processed_html = process_html_with_spacy(html_content, nlp_model, yaml_header)
    
    # Write the processed content to the output file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(processed_html)
    
    return f"Processed {filename}"

def process_files(input_folder, output_folder, nlp_model, testimonies_data):
    # Ensure output folder exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Get all HTML files in the input folder
    input_files = glob.glob(os.path.join(input_folder, '*.html'))
    input_files.sort()
    
    # Prepare arguments for each file
    args_list = [(input_path, 
                  os.path.join(output_folder, os.path.basename(input_path)), 
                  nlp_model, 
                  testimonies_data) for input_path in input_files]
    
    # Use multiprocessing to determine the number of CPUs
    num_workers = multiprocessing.cpu_count()
    
    # Process files using multithreading
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(process_single_file, args_list), total=len(args_list)))
    
    # Print summary
    processed = sum(1 for r in results if r.startswith("Processed"))
    skipped_existing = sum(1 for r in results if "already exists" in r)
    skipped_no_data = sum(1 for r in results if "no matching data found" in r)
    
    print(f"\nSummary:")
    print(f"Processed: {processed}")
    print(f"Skipped (already exists): {skipped_existing}")
    print(f"Skipped (no matching data): {skipped_no_data}")

# Load metadata
metadata = datasets.load_dataset("placingholocaust/testimony-metadata")["train"]
testimonies_metadata = pd.DataFrame(metadata)

# Setup spaCy model
labels = ["dlf", "populated place", "country", "region", "interior space", "env feature", "building", "spatial object"]
nlp = spacy.blank("en")
nlp.add_pipe("gliner_spacy", config={"gliner_model": "placingholocaust/gliner_small-v2.1-holocaust", "labels": labels, "chunk_size": 250})

# Usage example:
process_files("./data/03_html_sentences/", "./data/04_html_ner", nlp, testimonies_metadata)