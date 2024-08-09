import argparse
import json
import os
from mistralai import Mistral
from langchain_community.document_loaders import UnstructuredPDFLoader


def get_model_completion(mistral_api_key, user_prompt, system_prompt ='', json_mode=False, retries=3):

    try:
        api_key = os.environ["MISTRAL_API_KEY"]
        model = "mistral-large-latest"

        client = Mistral(api_key=api_key)
        
        messages = [
            {
                "role": "user",
                "content": user_prompt
            },
        ]

        if (system_prompt): 
            system_prompt_obj = {
                    "role": "system",
                    "content": system_prompt,
            }

            messages.insert(0, system_prompt_obj)

        success = False
        for i in range(retries): 
            if (json_mode): 
                chat_response = client.chat.complete(
                    model= model,
                    messages = messages,
                    response_format={
                        "type": "json_object",
                    },
                )
            else:
                chat_response = client.chat.complete(
                    model= model,
                    messages = messages,
                )

            if (chat_response.choices[0].message.content):
                success = True
                break

        if (success): 
            if chat_response:
                choices = chat_response.choices
                if isinstance(choices, list) and choices:
                    first_choice = choices[0]
                    message = first_choice.message
                    if message:
                        content = message.content
                        if content:
                            return chat_response.choices[0].message.content

    except Exception as e:
        print('Error in getting response from LLM: ', e)


def read_pdf(file_path):
    try: 
        loader = UnstructuredPDFLoader(file_path)
        data = loader.load()
        if data:
            document =  data[0]
            page_content = document.page_content
            if (page_content): 
                return page_content
            else: 
                return ''
        else: 
            return ''
        
    except Exception as e:
        print('Error in reading data from pdf: ', e)
        return ''


def extract_details_from_invoice(file_path, mistral_api_key=''): 

    if (not mistral_api_key): 
        mistral_api_key = os.environ["MISTRAL_API_KEY"]

    print('> Reading Uploaded File')

    invoice_content = read_pdf(file_path)
    print('> Invoice Content Read!')
    
    system_prompt = """
    You are an AI Assistant tasked with extracting detailed information from invoices provided by the user. If the given information is not an invoice, simply return \{\}. Your objective is to deliver highly accurate and structured data in the following JSON format:

{
  "customer_details": {
    "name": string,
    "address": string,
    "phone": string,
    "email": string,
    "additional_fields": dict
  },
  "products": [
    {
      "name": string,
      "quantity": int,
      "rate": float,
      total: float,
      "additional_fields": dict
    }
  ],
  "total_amount": {
    "amount": float,
    "currency": string
  }
}
    """

    user_prompt = invoice_content

    print('> Calling LLM for extracting details')

    response = get_model_completion(mistral_api_key=mistral_api_key, user_prompt=user_prompt, system_prompt=system_prompt, json_mode=True)

    try:
        print(response)
        invoice_details = json.loads(response)
        print(invoice_details)
        return invoice_details
    
    except Exception as e: 
        raise Exception('Error in Extracting Details from Invoice: ', e)

def save_extracted_data(data, output_path):
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Extract invoice details from a PDF file.")
    
    parser.add_argument(
        'source', 
        type=str, 
        help="Path to the PDF file from which to extract invoice details."
    )
    
    parser.add_argument(
        'destination', 
        type=str, 
        nargs='?',
        help="Output file path to store extracted details (optional). Defaults to '<file_name>-extracted.json' in the current directory."
    )
    
    args = parser.parse_args()

    if not os.path.isfile(args.source):
        print(f"Error: The file '{args.source}' does not exist.")
        exit(1)
    
    file_name = os.path.splitext(os.path.basename(args.source))[0]
    default_output_path = f'{file_name}-extracted.json'
    output_path = args.destination if args.destination else default_output_path

    extracted_data = extract_details_from_invoice(args.source)
    save_extracted_data(extracted_data, output_path)

    print(f"Invoice details extracted to '{output_path}'.")

if __name__ == "__main__":
    main()