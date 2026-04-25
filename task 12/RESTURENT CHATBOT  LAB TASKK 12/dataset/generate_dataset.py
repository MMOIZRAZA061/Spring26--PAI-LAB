import csv
import os

BASE_DIR = os.path.dirname(__file__)
OUT = os.path.join(BASE_DIR, '..', 'data', 'qna.csv')

# Short pool of core QA templates and answer fragments
questions_base = [
    "What are your opening hours",
    "When are you open",
    "What time do you open",
    "What time do you close",
    "Do you offer delivery",
    "Can I get home delivery",
    "How can I cancel my order",
    "How long does delivery take",
    "What pizzas do you have",
    "Do you have vegetarian options",
    "Is there a kids menu",
    "Do you take reservations",
    "How do I reserve a table",
    "Do you have gluten-free options",
    "Are you halal",
    "What payment methods do you accept",
    "Do you offer discounts",
    "What's on the menu today",
    "Do you serve alcohol",
    "Is parking available",
    "Can I order online",
    "Do you offer catering",
    "Do you have a loyalty program",
    "What desserts do you have",
    "Do you offer vegan options",
    "Are tables available tonight",
    "Can I change my order",
    "What's the phone number",
    "Where are you located",
    "Do you have outdoor seating",
    "Is WiFi available",
]

answers_base = [
    "We are open from 11 AM to 12 AM daily.",
    "Yes, we offer home delivery in the local area.",
    "To cancel, please call 0300-1234567 within 5 minutes of placing your order.",
    "Delivery usually takes 30-45 minutes depending on traffic.",
    "We have Chicken Tikka, Fajita, and Cheese pizza varieties.",
    "Yes — vegetarian and vegan options are available.",
    "Yes, we have a kids menu with smaller portions.",
    "Yes, you can reserve online or call us to book a table.",
    "We offer gluten-free options on request.",
    "Yes — all food is prepared halal.",
    "We accept cash, card, and online wallets.",
    "We run seasonal discounts; check our website for current offers.",
    "Today's specials are updated on the menu board and website.",
    "We serve soft drinks and some alcoholic beverages where permitted.",
    "Yes, there is parking available nearby at our premises.",
    "Orders can be placed via our website or by phone.",
    "We provide catering for events; contact our sales team for quotes.",
    "Join our loyalty program to collect points and rewards.",
    "We have ice cream, brownies, and cakes for dessert.",
    "Yes — outdoor seating is available subject to weather and booking.",
    "Free WiFi is available for customers.",
    "Our phone number is 0300-1234567.",
    "We are located in the main city center — follow the map on our site.",
]

# Variation tokens to create many unique question forms
prefixes = ["", "Hi, ", "Hello, ", "Hey, ", "Can you tell me", "Please tell me", "Quick question:"]
endings = ["?", " please?", " — thanks.", ".", " right now?"]
phrasing_mods = ["", " today", " tonight", " this weekend", " tomorrow"]

# Ensure output directory
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)

rows = []
idx = 0
# Create diverse variations
for p in prefixes:
    for q in questions_base:
        for pm in phrasing_mods:
            for e in endings:
                question = (p + q + pm + e).strip()
                # choose an answer by mapping common keywords
                ans = None
                qlower = q.lower()
                if any(k in qlower for k in ['hour', 'open', 'close', 'time']):
                    ans = "We are open from 11 AM to 12 AM daily."
                elif 'delivery' in qlower or 'home' in qlower:
                    ans = "Yes, we offer home delivery in the local area."
                elif 'cancel' in qlower or 'change' in qlower:
                    ans = "To cancel, please call 0300-1234567 within 5 minutes of placing your order."
                elif 'pizza' in qlower or 'pizzas' in qlower:
                    ans = "We have Chicken Tikka, Fajita, and Cheese pizza varieties."
                elif 'vegetarian' in qlower or 'vegan' in qlower:
                    ans = "Yes — vegetarian and vegan options are available."
                elif 'kids' in qlower:
                    ans = "Yes, we have a kids menu with smaller portions."
                elif 'reserve' in qlower or 'reservation' in qlower or 'book' in qlower:
                    ans = "Yes, you can reserve online or call us to book a table."
                elif 'gluten' in qlower:
                    ans = "We offer gluten-free options on request."
                elif 'halal' in qlower:
                    ans = "Yes — all food is prepared halal."
                elif 'payment' in qlower or 'pay' in qlower or 'card' in qlower:
                    ans = "We accept cash, card, and online wallets."
                elif 'discount' in qlower or 'offer' in qlower:
                    ans = "We run seasonal discounts; check our website for current offers."
                elif 'special' in qlower or 'menu' in qlower:
                    ans = "Today's specials are updated on the menu board and website."
                elif 'alcohol' in qlower or 'drink' in qlower:
                    ans = "We serve soft drinks and some alcoholic beverages where permitted."
                elif 'parking' in qlower:
                    ans = "Yes, there is parking available nearby at our premises."
                elif 'order' in qlower or 'online' in qlower:
                    ans = "Orders can be placed via our website or by phone."
                elif 'catering' in qlower:
                    ans = "We provide catering for events; contact our sales team for quotes."
                elif 'loyalty' in qlower or 'rewards' in qlower:
                    ans = "Join our loyalty program to collect points and rewards."
                elif 'dessert' in qlower or 'desserts' in qlower:
                    ans = "We have ice cream, brownies, and cakes for dessert."
                elif 'outdoor' in qlower:
                    ans = "Yes — outdoor seating is available subject to weather and booking."
                elif 'wifi' in qlower:
                    ans = "Free WiFi is available for customers."
                elif 'phone' in qlower or 'contact' in qlower:
                    ans = "Our phone number is 0300-1234567."
                elif 'where' in qlower or 'located' in qlower or 'location' in qlower:
                    ans = "We are located in the main city center — follow the map on our site."
                else:
                    # fallback
                    ans = "Please contact us at 0300-1234567 for details."

                rows.append({'question': question, 'answer': ans})
                idx += 1
                if idx >= 1200:
                    break
            if idx >= 1200:
                break
        if idx >= 1200:
            break
    if idx >= 1200:
        break

# Write CSV
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['question','answer'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f'Wrote {len(rows)} rows to {OUT}')