from report_processor import process_report
from IPython.display import display, Markdown

result = process_report("sample_report.png")  # or .pdf
display(result)