import glob
import pandas as pd
import os
from bs4 import BeautifulSoup


def clean_html(input_file):
    # Read the removal data
    with open('../assets/remove.txt', 'r') as f:
        remove = [line.strip() for line in f]

    # Read the input HTML file
    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Function to split and create new elements
    def split_dialogue(element):
        content = element.decode_contents()
        # Split on both <p> tags and Q:/A: markers
        parts = re.split(r'(<p>|(?<=</p>))|\s*(Q:|A:)', content, flags=re.IGNORECASE)
        parts = [p for p in parts if p and p.strip()]  # Remove empty parts

        if len(parts) > 1:
            print(f"Splitting dialogue in file: {input_file}")
            new_elements = []
            current_content = ""
            current_class = ""
            in_p_tag = False

            for part in parts:
                if part.strip().lower() in ['q:', 'a:']:
                    if current_content:
                        if not in_p_tag:
                            current_content = f"<p>{current_content}</p>"
                        new_element = BeautifulSoup(f'<dialogue class="{current_class}">{current_content}</dialogue>', 'html.parser')
                        new_elements.append(new_element)
                        current_content = ""
                    current_class = 'Question' if part.lower() == 'q:' else 'Answer'
                    current_content = f"<p>{part}"
                    in_p_tag = True
                elif part.strip() == '<p>':
                    in_p_tag = True
                    if current_content and not current_content.endswith('</p>'):
                        current_content += '</p>'
                    current_content += '<p>'
                else:
                    current_content += part
                    if part.endswith('</p>'):
                        in_p_tag = False

            if current_content:
                if not in_p_tag:
                    current_content = f"<p>{current_content}</p>"
                new_element = BeautifulSoup(f'<dialogue class="{current_class}">{current_content}</dialogue>', 'html.parser')
                new_elements.append(new_element)

            return new_elements
        return None

    # Find and process dialogue classes
    dialogue_classes = soup.find_all('dialogue')
    for dialogue in dialogue_classes:
        new_elements = split_dialogue(dialogue)
        if new_elements:
            for new_element in new_elements:
                dialogue.insert_before(new_element)
            dialogue.decompose()

    # Remove strings from the remove list
    for string in soup.strings:
        if any(remove_str in string for remove_str in remove):
            string.replace_with('')

    # Create output directory if it doesn't exist
    output_dir = '../data/cleaned_htmls'
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename
    input_filename = os.path.basename(input_file)
    output_filename = f"{os.path.splitext(input_filename)[0]}_cleaned.html"
    output_path = os.path.join(output_dir, output_filename)

    # Save the cleaned HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"Cleaned HTML saved to: {output_path}")


# process htmls
html_files = glob.glob("../data/pdfs/*.html")
approved_files = []
for filename in html_files:
    if "sum" not in filename and "trs_en" in filename:
        approved_files.append(filename)

for filename in approved_files:
    clean_html(filename)