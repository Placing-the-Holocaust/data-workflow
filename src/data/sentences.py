import os
from bs4 import BeautifulSoup
import spacy

def add_sentences(input_directory, output_directory):
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.endswith(".html"):
            input_filepath = os.path.join(input_directory, filename)
            output_filepath = os.path.join(output_directory, filename)

            with open(input_filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            soup = BeautifulSoup(content, 'html.parser')
            sentence_id = 1

            # Remove empty p tags
            for p in soup.find_all('p'):
                if not p.get_text(strip=True):
                    p.decompose()

            for dialogue in soup.find_all('dialogue'):
                for p in dialogue.find_all('p'):
                    text = p.get_text()
                    doc = nlp(text)
                    
                    new_content = []
                    for sent in doc.sents:
                        new_content.append(f'<sentence id="{sentence_id}">{sent.text} </sentence>')
                        sentence_id += 1
                    
                    p.clear()
                    p.extend(BeautifulSoup(''.join(new_content), 'html.parser'))

            # Remove empty dialogue tags
            for dialogue in soup.find_all('dialogue'):
                if not dialogue.find('p'):
                    dialogue.decompose()

            # Save the modified content to the output directory
            with open(output_filepath, 'w', encoding='utf-8') as file:
                file.write(str(soup))

            print(f"Processed {filename} and saved to {output_filepath}")