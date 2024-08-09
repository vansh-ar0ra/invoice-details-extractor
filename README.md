# Invoice Details Extractor

This repository contains a Python script - invoice_details_extractor.py designed to extract invoice details from PDF files. The script can be run as a command line tool, allowing users to specify the source PDF file and optionally, the destination for the extracted data.
In addition to the command-line tool, this repository includes a Streamlit application that demonstrates the usage of the Invoice Details extractor. You can access the live demo at [this link](https://vansh-swipe-invoice-extractor.streamlit.app/).


## Objective

The objective of this repository is to provide a tool for extracting and saving invoice details from PDF files. This is particularly useful for automating the process of parsing and storing invoice data in a structured format.

## Prerequisites

- Python 3.x
- Virtual Environment (optional but recommended)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a Virtual Environment

It is recommended to create a virtual environment to manage dependencies:

```bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install the Required Packages

Install the necessary dependencies using pip:

```bash
pip install -r requirements.txt
```

Make sure to update requirements.txt with any necessary libraries that your script requires, such as PyPDF2 or any other package you use for PDF extraction.


### 4. Add MISTRAL_API_KEY to environmental variables

```bash
export MISTRAL_API_KEY=<your-mistral-api-key>
```

## Usage
The script can be run directly from the command line. Below is the basic usage:

```bash
python invoice_details_extractor.py <source> [destination]
```

### Arguments

source (required): Path to the PDF file from which to extract invoice details.
destination (optional): Output file path to store extracted details. If not provided, the data will be saved in the current directory with the name <file_name>-extracted.json.

### Example

Extracting data from invoice.pdf and saving it to invoice-details.json:

```bash
python invoice_extractor.py /path/to/invoice.pdf /path/to/output/invoice-details.json
```

If no destination is provided, it will default to the current directory:

```bash
python invoice_extractor.py /path/to/invoice.pdf
```

This will save the extracted data to invoice-extracted.json in the current directory.

### Error Handling

The script checks if the source file exists. If the source file is missing or not a valid file, it will throw an error.