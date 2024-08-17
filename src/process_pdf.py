import json
import os
import concurrent.futures
from functools import partial
from tqdm import tqdm
from ushmm import pdf_to_images, images_to_text, clean_texts, remove_footers, process_testimony_texts
from huggingface_hub import hf_hub_download, list_repo_files
from datasets import load_dataset
import re



def process_pdf(pdf_filename, pdfs_directory="../data", errors_file="errors.json"):
    clean_filename = pdf_filename.replace('.pdf', '')
    output_html_path = os.path.join(pdfs_directory, f"{clean_filename}.html")
    
    # Load existing errors
    if os.path.exists(errors_file):
        with open(errors_file, 'r') as f:
            errors = json.load(f)
    else:
        errors = []
    
    # Skip if already processed or in error list
    if os.path.exists(output_html_path) or pdf_filename in errors:
        return f"Skipping {clean_filename} as it's already processed or in error list."
    
    try:
        if "pdfs" in pdf_filename:
            hf_hub_download(repo_id="placingholocaust/ushmm-pdfs", filename=pdf_filename, local_dir=pdfs_directory, repo_type="dataset")
            
            images = pdf_to_images(os.path.join(pdfs_directory, pdf_filename), 
                                   os.path.join(pdfs_directory, clean_filename, "images"), save=True)
            cropped_images = remove_footers(os.path.join(pdfs_directory, clean_filename, "images"), 
                                            output_directory=os.path.join(pdfs_directory, clean_filename, "images_cropped"), save=True)
            texts = images_to_text(os.path.join(pdfs_directory, clean_filename, "images_cropped"), 
                                   save=True, output_folder=os.path.join(pdfs_directory, clean_filename, "text"))
            texts = clean_texts(os.path.join(pdfs_directory, clean_filename, "text"), 
                                save=True, output_directory=os.path.join(pdfs_directory, clean_filename, "clean_text"))
            html_result = process_testimony_texts(os.path.join(pdfs_directory, clean_filename, "clean_text"), 
                                                  output_file=output_html_path, save=True)
            return f"Processed {clean_filename} and saved HTML output."
    except Exception as e:
        # Add to error list if not already present
        if pdf_filename not in errors:
            errors.append(pdf_filename)
            with open(errors_file, 'w') as f:
                json.dump(errors, f)
        return f"Error processing {clean_filename}: {str(e)}"

def main(pdfs, rgs, max_workers=None):
    # Filter PDFs based on RG numbers
    filtered_pdfs = [pdf for pdf in pdfs if any(rg in pdf for rg in rgs)]
    
    print(f"Original number of PDFs: {len(pdfs)}")
    print(f"Final number of PDFs after filtering: {len(filtered_pdfs)}")
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        process_pdf_with_dir = partial(process_pdf, pdfs_directory="./data")
        executor.map(process_pdf_with_dir, filtered_pdfs)
    


if __name__ == "__main__":
    repo_id = "placingholocaust/ushmm-pdfs"
    pdfs = list_repo_files(repo_id, repo_type="dataset")
    print("Sample of original PDFs:")
    print(pdfs[:10])
    
    # Load RG numbers from the metadata dataset
    rgs_dataset = load_dataset("placingholocaust/testimony-metadata")["train"]["RG Number"]
    
    # Clean RG numbers to match the format in PDF filenames
    rgs = [re.sub(r'[^\w.-]', '', rg) for rg in rgs_dataset]
    
    print("\nSample of RG numbers from metadata:")
    print(rgs[:10])
    
    main(pdfs, rgs)