import csv
import os
import random

BASE_DIR = os.path.dirname(__file__)
IN_PATH = os.path.join(BASE_DIR, '..', 'data', 'qna.csv')
OUT_PATH = IN_PATH

# Load existing rows
rows = []
if os.path.exists(IN_PATH):
    with open(IN_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({'question': r['question'].strip(), 'answer': r['answer'].strip()})

existing_qs = set(r['question'] for r in rows)

# Expanders and tokens
intents = {
    'hours': ["what are your hours", "when do you open", "closing time", "operating hours", "open hours"],
    'delivery': ["do you deliver", "home delivery", "delivery time", "deliver to my area"],
    'menu': ["what's on the menu", "show menu", "menu items", "menu today", "specials"],
    'pizza': ["pizza types", "pizza flavours", "which pizzas", "pizza options"],
    'reservation': ["reserve table", "book a table", "table booking", "how to reserve"],
    'payment': ["payment methods", "do you accept cards", "cash or card", "online payment"],
    'cancellation': ["cancel order", "how to cancel", "change my order", "modify order"],
    'parking': ["parking available", "is parking there", "valet parking"],
    'diet': ["vegetarian options", "vegan options", "gluten free", "allergy info", "nut free"],
    'contact': ["phone number", "contact info", "address", "where are you located", "location"],
    'catering': ["do you cater", "catering services", "event catering"],
    'offers': ["discount", "promo code", "coupon", "offers"],
    'kids': ["kids menu", "high chair", "play area"],
    'access': ["wheelchair access", "accessible seating", "ramps"],
}

prefixes = ["", "Hi, ", "Hello, ", "Please, ", "Could you ", "Can you ", "Hey "]
endings = ["?", " please?", " asap?", " — thanks.", " now?", "."]
local_tokens = ["batao", "kahan", "kaha", "kahan ho", "address batao", "location batao"]
text_variations = ["pls", "please", "plz", "kindly"]

answers_map = {
    'hours': "We are open from 11 AM to 12 AM daily.",
    'delivery': "Yes, we offer home delivery in the local area.",
    'menu': "We offer pizza, burgers, pasta, BBQ, and desserts.",
    'pizza': "We have Chicken Tikka, Fajita, and Cheese Pizza.",
    'reservation': "You can reserve online or call us to book a table.",
    'payment': "We accept cash, card, and online wallets.",
    'cancellation': "To cancel, please call 0300-1234567 within 5 minutes of placing your order.",
    'parking': "There is parking available nearby.",
    'diet': "We have vegetarian and gluten-free options on request.",
    'contact': "Our phone number is 0300-1234567 and we are in the main city center.",
    'catering': "Yes, we provide catering—contact sales for a quote.",
    'offers': "We run seasonal discounts; check our website for current offers.",
    'kids': "Yes, we have a kids menu and high chairs available.",
    'access': "Wheelchair access is available; let us know if you need assistance.",
}

# Function to generate paraphrases
def generate_paraphrases(target_count=5000):
    out = []
    idx = 0
    keys = list(intents.keys())
    random.seed(42)
    while len(existing_qs) + len(out) < target_count:
        intent = random.choice(keys)
        q_template = random.choice(intents[intent])
        prefix = random.choice(prefixes)
        ending = random.choice(endings)
        # occasionally insert local token
        if random.random() < 0.12:
            lt = random.choice(local_tokens)
            question = f"{prefix}{q_template} {lt}{ending}"
        else:
            # add variation words
            if random.random() < 0.15:
                q_template = q_template + " " + random.choice(text_variations)
            question = f"{prefix}{q_template}{ending}"
        question = question.strip()
        if question not in existing_qs and question not in (r['question'] for r in out):
            out.append({'question': question, 'answer': answers_map[intent]})
        idx += 1
        if idx > target_count * 5:
            break
    return out

if __name__ == '__main__':
    add = generate_paraphrases(5000)
    print(f'Generated {len(add)} new questions (target total 5000).')
    # append to CSV
    with open(OUT_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['question','answer'])
        for r in add:
            writer.writerow({'question': r['question'], 'answer': r['answer']})
    print('Appended generated questions to', OUT_PATH)