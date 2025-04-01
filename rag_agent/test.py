import requests

BASE_URL = "http://localhost:8000"

def test_root():
    url = f"{BASE_URL}/"
    response = requests.get(url)
    try:
        data = response.json()
    except Exception as e:
        data = response.text
    print("Root endpoint response:")
    print(data)
    print("-" * 50)

def test_ingest():
    # Adjust pdf_path to a valid PDF file path if you want to test ingestion.
    payload = {"pdf_path": r"pdf\new-employee-handbook.pdf"}
    url = f"{BASE_URL}/ingest"
    response = requests.post(url, json=payload)
    try:
        data = response.json()
    except Exception as e:
        data = response.text
    print("Ingest endpoint response:")
    print(data)
    print("-" * 50)

def test_query():
    question = "How is accident leave calculated and approved?"
    payload = {"query": question}
    url = f"{BASE_URL}/query"
    response = requests.post(url, json=payload)
    try:
        data = response.json()
    except Exception as e:
        data = response.text
        print("Error decoding JSON response:", e)
    print("Query endpoint response:")
    print(data)
    print("-" * 50)

if __name__ == "__main__":
    test_root()
    # Uncomment the next line to test ingestion if you have a PDF.
    # test_ingest()
    test_query()
