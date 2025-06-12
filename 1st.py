import fitz  # PyMuPDF

pdf_url = "https://indiancitizenshiponline.nic.in/Documents/UserGuide/ic_faq_24092019.pdf"
pdf_file = "citizenship_faq.pdf"

# Download the PDF
import requests
response = requests.get(pdf_url)
with open(pdf_file, "wb") as file:
    file.write(response.content)

# Extract text from PDF
text = ""
with fitz.open(pdf_file) as doc:
    for page in doc:
        text += page.get_text() + "\n"

# Save the text to a file
with open("citizenship_faqs.txt", "w", encoding="utf-8") as file:
    file.write(text)

print("✅ PDF text extracted and saved!")
