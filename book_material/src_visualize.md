# src.visualization.visualize.py

```python
import diff_match_patch as dmp_module
from IPython.display import HTML, display

def compare_texts(text1, text2):
    """
    Compare two texts using diff-match-patch and return formatted HTML.
    """
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)
    
    html1 = []
    html2 = []

    for (op, data) in diffs:
        text = data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "&para;<br>")
        if op == dmp.DIFF_INSERT:
            html2.append(f"<span style='background-color: #2f4f4f; color: #98fb98;'>{text}</span>")  # Dark green background, light green text
        elif op == dmp.DIFF_DELETE:
            html1.append(f"<span style='background-color: #8b0000; color: #ffa07a;'>{text}</span>")  # Dark red background, light coral text
        else:
            html1.append(text)
            html2.append(text)
    
    return ''.join(html1), ''.join(html2)

def visualize_diff(text1, text2):
    """
    Compare texts and display the results side by side in a notebook.
    """
    formatted_text1, formatted_text2 = compare_texts(text1, text2)
    
    # Calculate similarity score
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    similarity_score = 1 - (dmp.diff_levenshtein(diffs) / max(len(text1), len(text2)))
    
    # Create HTML for side-by-side display
    html_content = f"""
    <div style="display: flex; font-family: Arial, sans-serif; background-color: #1e1e1e; color: #d4d4d4;">
        <div style="flex: 1; padding: 10px; border-right: 1px solid #555;">
            <h3>Original Text</h3>
            <div style="white-space: pre-wrap;">{formatted_text1}</div>
        </div>
        <div style="flex: 1; padding: 10px;">
            <h3>Modified Text</h3>
            <div style="white-space: pre-wrap;">{formatted_text2}</div>
        </div>
    </div>
    """
    
    print(f"Similarity Score: {similarity_score:.2f}")
    display(HTML(html_content))
    ```