import requests
from bs4 import BeautifulSoup

# List of government FAQ URLs
urls = [
    "https://careerairforce.gov.in/faqs",
    "https://www.data.gov.in/faqs",
    "https://www.mea.gov.in/cpv-faq-menu-01.htm",
    "https://www.india.gov.in/faqs-issues",
    "https://guidelines.india.gov.in/faqs/"
]

faq_data = ""

for url in urls:
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all FAQ text (Change tag if needed)
        faqs = soup.find_all(["p", "h2", "h3", "li"])  # Common tags for FAQs
        faq_data += "\n".join([faq.get_text() for faq in faqs]) + "\n\n"

# Save extracted FAQs to a file
with open("gov_faqs.txt", "w", encoding="utf-8") as file:
    file.write(faq_data)

print("✅ Web FAQs extracted and saved!")
from langchain.text_splitter import CharacterTextSplitter

# Read the extracted FAQs
with open("gov_faqs.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Split text into chunks
splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=500,  # Each chunk is 500 characters
    chunk_overlap=50  # Small overlap for context
)

chunks = splitter.split_text(text)

# Save the chunks into a file
with open("faq_chunks.txt", "w", encoding="utf-8") as file:
    file.write("\n\n".join(chunks))

print("✅ Text successfully split into chunks!")
import chromadb

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create a new collection for storing FAQs
collection = chroma_client.get_or_create_collection("government_faqs")

# Read the chunked FAQs
with open("faq_chunks.txt", "r", encoding="utf-8") as file:
    faq_chunks = file.readlines()

# Add each chunk to the database
for idx, chunk in enumerate(faq_chunks):
    collection.add(
        documents=[chunk.strip()],
        ids=[f"faq_{idx}"]
    )

print("✅ FAQs stored in ChromaDB successfully!")

