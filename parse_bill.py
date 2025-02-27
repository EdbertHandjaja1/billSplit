import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("Missing OpenAI API Key. Set it in .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def parse_bill_with_chatgpt(text):
    """
    Uses OpenAI GPT to extract item names and prices from the receipt text.
    Returns a JSON array of items.
    """
    prompt = f"""
    You are an AI that extracts item names and prices from receipts.
    Given the following text, extract a list of items and their corresponding prices.

    Text:
    {text}

    Return the data as a JSON array where each item has "name" and "price" fields.
    Example Output:
    [
        {{"name": "Apples", "price": 2.99}},
        {{"name": "Milk", "price": 3.50}},
        {{"name": "Bread", "price": 1.99}}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert text parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        extracted_data = response.choices[0].message.content.strip()
        return json.loads(extracted_data)

    except json.JSONDecodeError:
        print("Error: Could not parse JSON. Raw response:", extracted_data)
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def split_bill(items):
    """
    Prompts the user to specify how each item should be split among people.
    Returns a dictionary mapping each person to the amount they owe.
    """
    bill_split = {}

    print("\nHow should each item be split? (e.g., 'Alice 50% Bob 50%' or 'Alice 1 Bob 2')")

    for item in items:
        name = item["name"]
        price = item["price"]

        while True:
            print(f"\nItem: {name} - ${price:.2f}")
            split_input = input("Enter split (names and percentages or shares): ").strip()

            try:
                split_parts = split_input.split()
                total = 0
                split_info = {}

                for i in range(0, len(split_parts), 2):
                    person = split_parts[i]
                    share = split_parts[i + 1]

                    if "%" in share:
                        share = float(share.strip("%")) / 100
                    else:
                        share = float(share)

                    split_info[person] = share
                    total += share

                if total == 1 or all(isinstance(v, int) for v in split_info.values()):
                    break
                else:
                    print("Invalid split. Ensure total percentage sums to 100% or shares are valid.")

            except Exception as e:
                print("Invalid input format. Try again.")

        # Normalize shares if needed
        if sum(split_info.values()) != 1:
            total_shares = sum(split_info.values())
            split_info = {p: s / total_shares for p, s in split_info.items()}

        # Calculate what each person owes
        for person, fraction in split_info.items():
            amount = price * fraction
            bill_split[person] = bill_split.get(person, 0) + amount

    return bill_split

if __name__ == "__main__":
    # Read OCR extracted text
    with open("extracted_text.txt", "r") as f:
        extracted_text = f.read()

    parsed_items = parse_bill_with_chatgpt(extracted_text)

    if parsed_items:
        final_split = split_bill(parsed_items)
        print("\nFinal Amounts Owed:")
        for person, amount in final_split.items():
            print(f"{person} owes: ${amount:.2f}")
