from flask import Flask, request, jsonify, render_template
import re

# Chatbot patterns
pairs = [
    [r"hi|hello|hey", ["Welcome to our Restaurant 🍽️", "Hello! How can I help you today?"]],
    [r"(.*)menu(.*)", ["We offer pizza, burgers, pasta, BBQ, and desserts."]],
    [r"(.*)pizza(.*)", ["We have Chicken Tikka, Fajita, and Cheese Pizza 🍕"]],
    [r"(.*)burger(.*)", ["We serve Zinger, Beef, and Chicken burgers 🍔"]],
    [r"(.*)pasta(.*)", ["Creamy Alfredo and Spicy Pasta available 🍝"]],
    [r"(.*)bbq(.*)", ["BBQ includes tikka, seekh kebab, and malai boti 🍗"]],
    [r"(.*)dessert(.*)", ["We have ice cream, brownies, and cake 🍰"]],
    [r"(.*)drink(.*)", ["Cold drinks, juices, and shakes available 🥤"]],
    [r"(.*)price(.*)", ["Our prices are affordable. What item price do you want?"]],
    [r"(.*)timing(.*)|hours", ["We are open from 11 AM to 12 AM"]],
    [r"(.*)location(.*)", ["We are located in the main city center"]],
    [r"(.*)track(.*)order(.*)", ["To track your order, open our website's 'Track Order' page or call 0300-1234567 and provide your order ID."]],
    [r"(.*)order status(.*)", ["To check order status, use the 'Track Order' page on our site or call 0300-1234567 with your order number."]],
    [r"(.*)cancel (?:my )?order(.*)", ["You can cancel within 5 minutes after placing the order. Call 0300-1234567 with your order ID to cancel."]],
    [r"(.*)order(.*)", ["You can place order online or call 0300-1234567"]],
    [r"(.*)delivery(.*)", ["Yes! Home delivery available 🚚"]],
    [r"(.*)reservation(.*)", ["You can reserve a table by calling us"]],
    [r"(.*)family(.*)", ["Yes, we have a family hall 👨‍👩‍👧‍👦"]],
    [r"(.*)wifi(.*)", ["Yes, free WiFi available 📶"]],
    [r"(.*)parking(.*)", ["Parking space is available 🅿️"]],
    [r"(.*)discount(.*)", ["We offer weekend discounts 🎉"]],
    [r"(.*)offer(.*)", ["Today: Buy 1 Get 1 Free Pizza 🍕"]],
    [r"(.*)special(.*)", ["Our special is Chicken Karahi 🔥"]],
    [r"(.*)veg(.*)", ["Yes, vegetarian options available 🥗"]],
    [r"(.*)spicy(.*)", ["We can adjust spice level as per your choice 🌶️"]],
    [r"(.*)halal(.*)", ["Yes, all our food is 100% halal ✅"]],
    [r"(.*)chef(.*)", ["Our chefs are highly experienced 👨‍🍳"]],
    [r"(.*)clean(.*)", ["We maintain high hygiene standards 🧼"]],
    [r"(.*)payment(.*)", ["We accept cash, card, and online payments 💳"]],
    [r"(.*)card(.*)", ["Yes, card payment is accepted"]],
    [r"(.*)cash(.*)", ["Cash payment available"]],
    [r"(.*)online(.*)", ["Online payment via JazzCash/EasyPaisa available"]],
    [r"(.*)cancel(.*)", ["You can cancel order within 5 minutes"]],
    [r"(.*)refund(.*)", ["Refund available if order is incorrect"]],
    [r"(.*)complaint(.*)", ["We are sorry! Please call support: 0300-0000000"]],
    [r"(.*)feedback(.*)", ["We value your feedback 😊"]],
    [r"(.*)owner(.*)", ["Restaurant owned by Moiz Group"]],
    [r"(.*)branch(.*)", ["We have multiple branches in the city"]],
    [r"(.*)takeaway(.*)", ["Takeaway service available"]],
    [r"(.*)kids(.*)", ["Kids play area available 🎈"]],
    [r"(.*)music(.*)", ["Live music available on weekends 🎶"]],
    [r"(.*)thank you|thanks", ["You're welcome! Enjoy your meal 😊"]],
    [r"bye|goodbye", ["Goodbye! Visit again 👋"]],
    [r"(.*)catering(.*)", ["We provide catering for events; call 0300-1234567 for quotes."]],
    [r"(.*)private event(.*)", ["Yes, we host private events and parties; ask for manager."]],
    [r"(.*)gift card(.*)", ["Gift cards are available at the counter and online."]],
    [r"(.*)loyalty(.*)|rewards(.*)", ["Join our loyalty program for points and free items."]],
    [r"(.*)chef special(.*)", ["Today's chef special is Butter Garlic Prawn 🦐"]],
    [r"(.*)today(.*)special(.*)", ["Today's specials: Butter Garlic Prawn, BBQ Platter, and Molten Cake."]],
    [r"(.*)breakfast(.*)", ["Breakfast menu available 8 AM - 11 AM: omelettes, pancakes, and more."]],
    [r"(.*)brunch(.*)", ["Brunch is served on weekends with special combos."]],
    [r"(.*)allergen(.*)|allergy(.*)", ["Please tell us your allergy and we'll advise safe menu items."]],
    [r"(.*)gluten(.*)free(.*)", ["We offer gluten-free pasta and bread on request."]],
    [r"(.*)vegan(.*)", ["Vegan options: grilled vegetables, vegan burger, and salads."]],
    [r"(.*)nutrition(.*)|calorie(.*)", ["Nutritional info is available on request for most dishes."]],
    [r"(.*)kids menu(.*)", ["Kids menu has small portions and healthy options."]],
    [r"(.*)high chair(.*)|child seat(.*)", ["We provide high chairs and child seats upon request."]],
    [r"(.*)birthday(.*)cake(.*)", ["We can prepare a birthday cake; pre-order 24 hours in advance."]],
    [r"(.*)anniversary(.*)", ["We can arrange special desserts and a decorated table."]],
    [r"(.*)live sports(.*)|tv(.*)", ["We show live sports on big screens during major events."]],
    [r"(.*)outdoor(.*)seating(.*)", ["Outdoor seating available; book ahead on busy nights."]],
    [r"(.*)view(.*)", ["We have a rooftop with city view (subject to availability)."]],
    [r"(.*)ambience(.*)", ["Casual, family-friendly ambience with soft music."]],
    [r"(.*)dress code(.*)", ["No strict dress code; smart casual recommended for evenings."]],
    [r"(.*)group booking(.*)", ["For groups of 10+, please call to reserve a table."]],
    [r"(.*)corporate(.*)order(.*)", ["We handle corporate catering and large orders; contact sales."]],
    [r"(.*)promo code(.*)|coupon(.*)", ["Enter promo codes at checkout or show them in-store."]],
    [r"(.*)pet friendly(.*)", ["We allow small pets in outdoor seating only."]],
    [r"(.*)accessibility(.*)|wheelchair(.*)", ["Wheelchair access available; let us know if you need assistance."]],
    [r"(.*)contact(.*)|phone(.*)", ["You can call us at 0300-1234567 or email info@restaurant.example"]],
    [r"(.*)pickup(.*)|takeout time(.*)", ["Pickup orders are ready in 15-20 minutes depending on items."]],
    [r"(.*)parking valet(.*)", ["Valet parking is available during peak hours."]],
    [r"(.*)private dining(.*)", ["Private dining rooms can be booked for special occasions."]],
    [r"(.*)reservation online(.*)", ["You can reserve online via our website or call us directly."]],
    [r"(.*)ingredients(.*)", ["If you want ingredients list for a dish, we can provide it on request."]],
    [r"(.*)soup(.*)", ["We have tomato basil, chicken noodle, and daily special soups."]],
    [r"(.*)salad(.*)", ["Fresh salads: Caesar, Greek, and House salad with house dressing."]],
    [r"(.*)steak(.*)", ["Steaks cooked to order: rare, medium, or well-done — served with sides."]],
    [r"(.*)seafood(.*)", ["Seafood menu includes grilled fish, prawns, and calamari."]],
    [r"(.*)sushi(.*)", ["We offer sushi rolls on select days — check today's menu."]],
    # Important extra patterns and language variants
    [r"(.*)contact no plz(.*)", ["You can call us at 0300-1234567."]],
    [r"(.*)contact no batao(.*)", ["You can call us at 0300-1234567."]],
    [r"(.*)phone(.*)number(.*)", ["You can call us at 0300-1234567."]],
    [r"(.*)location share kero(.*)", ["We are located in the main city center"]],
    [r"(.*)kahan ho(.*)|(.*)location(.*)", ["We are located in the main city center"]],
    [r"(.*)drinks name(.*)|(.*)drink names(.*)|(.*)what (.*)drinks(.*)", ["Cold drinks: Coke, Sprite, Fanta; Juices: Mango, Orange; Shakes: Chocolate, Vanilla 🥤"]],
    [r"(.*)juice(.*)|(.*)jusic.*|(.*)jusices(.*)", ["We have Mango juice, Orange juice, and seasonal fresh juices."]],
    [r"(.*)do you have juices(.*)", ["Yes — Mango, Orange, Apple and seasonal fresh juices are available."]],
    [r"(.*)drinks availab.*(.*)", ["Cold drinks, juices, and shakes available 🥤"]],
    [r"nice|good|great|awesome", ["Thanks! Glad you liked it 🙂"]],
    [r"how are you(.*)", ["I'm a friendly bot — ready to help you with the menu and reservations."]],
    [r"(.*)menu items(.*)|(.*)what (.*)do you serve(.*)", ["We serve pizza, burgers, pasta, BBQ, salads, seafood, steaks and desserts."]],
    [r"(.*)burger names(.*)|(.*)which burgers(.*)", ["We have Zinger, Beef, Chicken, and Veggie burgers."]],
    [r"(.*)where are you located(.*)", ["We are located in the main city center"]],
    [r"(.*)working hours(.*)|(.*)open(.*)hours(.*)", ["We're open from 11 AM to 12 AM daily."]],
    [r"(.*)reservation online(.*)", ["You can reserve online via our website or call us at 0300-1234567."]],
    [r"(.*)thank you|thanks(.*)", ["You're welcome! Enjoy your meal 😊"]],
]

# Initialize chatbot: try to use NLTK Chat, otherwise use a simple regex-based fallback
try:
    from nltk.chat.util import Chat as NLTKChat
    chatbot = NLTKChat(pairs)
except Exception:
    class ChatFallback:
        def __init__(self, pairs_list):
            self.pairs = [(re.compile(p, re.I), resp) for p, resp in pairs_list]
        def respond(self, message):
            if not message:
                return None
            for pattern, resp in self.pairs:
                try:
                    if pattern.search(message):
                        return resp[0] if isinstance(resp, (list, tuple)) else resp
                except re.error:
                    continue
            return None

    chatbot = ChatFallback(pairs)

# Keyword fallback map (helps with accuracy when regex doesn't match)
app = Flask(__name__, static_folder='static', template_folder='templates')
import difflib


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    message = data.get('message', '')
    try:
        response = chatbot.respond(message)
    except Exception:
        response = None

    if not response:
        response = "Sorry, I didn't understand. Could you rephrase?"

    return jsonify({'response': response})


 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
