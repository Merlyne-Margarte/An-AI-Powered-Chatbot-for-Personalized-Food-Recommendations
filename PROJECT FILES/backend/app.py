from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Food
from rapidfuzz import process
from huggingface_hub import InferenceClient
import random
import os
import time
from dotenv import load_dotenv
load_dotenv()



CUISINES = [
    "indian",
    "south indian",
    "north indian",
    "continental",
    "american",
    "indo-chinese",
    "western"
]


app = Flask(__name__)
CORS(app)

# SQLAlchemy setup
engine = create_engine('sqlite:///food.db', echo=False)
Session = sessionmaker(bind=engine)

# Store user data (simple session)
user_data = {
    "name": "",
    "diet": "",
    "spice": "",
    "meal": "",
    "goal":"",
    "allergy": None,
    "dislikes": []
}

nutrition_tracker = {
    "calories":0,
    "protein":0
}

last_food = ""

last_plan = ""

conversation_history = []

@app.route("/")
def home():
   return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message", "").lower()

    print("Message received:", message)
    print("User data:", user_data)

    global last_food
    global last_plan

#rolling conversation history to understand context
    conversation_history.append(message)
    if len(conversation_history)>5:
        conversation_history.pop(0)

    selected_cuisine = None

    
    for cuisine in CUISINES:
        if cuisine in message:
            selected_cuisine = cuisine
            break

    # Step 1: Capture name
    if user_data["name"] == "":
        user_data["name"] = message
        return jsonify({
            "reply": f"Nice to meet you, {message.capitalize()} 😊 Are you Veg or Non-Veg?"
        })

    # THANK YOU RESPONSE
    if "thank" in message:
        return jsonify({"reply": "😊 You're welcome! Happy to help!"})

    # Greeting (safe check)
    if message in ["hello", "hi", "hey"]:
        return jsonify({
            "reply": f"Hello {user_data['name'].capitalize()}! How can I help you with food today? 😊"
        })
    
    if "diet plan" in message or "plan my meals" in message or "plan" in message:
        plan = generate_diet_plan()
        return jsonify({"reply": plan})
    
    if "nutrition summary" in message or "summary" in message:

        return jsonify({
            "reply":(
                "📊 Nutrition Summary\n\n"
                f"🔥 Calories consumed: {nutrition_tracker['calories']} kcal\n"
                f"💪 Protein consumed: {nutrition_tracker['protein']} g"
            )
        })
    if "show" in message and "cuisines" in message:

        cuisine_list = "\n".join([c.title() for c in CUISINES])

        return jsonify({
            "reply": f"🌎 Available cuisines:\n\n{cuisine_list}"
        })
    for cuisine in CUISINES:
        if f"show {cuisine}" in message:

            session = Session()

            foods = session.query(Food).filter_by(cuisine=cuisine).all()

            session.close()

            if not foods:
                return jsonify({"reply": "No dishes found."})

            suggestions = random.sample(foods, min(3,len(foods)))

            result = f"🍜 Popular {cuisine.title()} dishes:\n\n"

            for f in suggestions:
                result += f"• {f.name}\n"

            return jsonify({"reply": result})
        
            
    
    if any(word in message for word in ["why","benefit","nutrition","good","advantage"]):
        
        if last_plan:
            explanation = ai_food_chat(message, last_plan)
            return jsonify({"reply": explanation})

        if last_food:
            explanation = ai_food_chat(message, last_food)
            return jsonify({"reply": explanation})
        
        return jsonify({"reply":"Ask for a food recommendation first 😊"})
        

    # Next recommendation
    if "next" in message or "another" in message:
        session = Session()
        foods = session.query(Food).all()
        last_plan=""
    
        # remove last recommended food
        foods = [f for f in foods if f.name not in last_food]

        if user_data["allergy"]:
            foods = [f for f in foods if user_data["allergy"] not in (f.allergens or "")]

        if not foods:
            session.close()
            return jsonify({"reply": "😔 No more recommendations available."})

        selected_food = random.choice(foods)

        result = (
            f"\n🎯 Another option for you:\n"
            f"🍽️ Try {selected_food.name}\n"
            f"Cuisine: {selected_food.cuisine.title()}\n"
            f"Calories: {selected_food.calories} kcal\n"
            f"Protein: {selected_food.protein} g"
        )

        last_food = selected_food.name

        session.close()

        return jsonify({"reply": result})
        
    
    def match_word(user_word, options):
        match = process.extractOne(user_word, options)
        if match and match[1] > 70:
            return match[0]
        return None
    
    #diet = match_word(message, ["veg", "non veg", "nonveg"])
    spice = match_word(message, ["spicy", "mild"])
    meal = match_word(message, ["breakfast", "lunch", "dinner"])
    goal = match_word(message, ["muscle gain", "weight loss", "healthy", "protein rich", "high protein", "diet","low calorie","fit", "normal"])

    if "nonveg" in message or "non veg" in message:
        user_data["diet"] = "non veg"
    elif "veg" in message:
        user_data["diet"] = "veg"

    if spice:
        user_data["spice"] = spice

    if meal:
        user_data["meal"] = meal

    if goal:
        if "protein" in goal or "muscle" in goal or "fit" in goal:
            user_data["goal"] = "muscle gain"
        elif "weight" in goal or "healthy" in goal or "diet" in goal or "low" in goal:
            user_data["goal"] = "weight loss"
        elif "normal" in goal:
            user_data["goal"] = "normal"
    
    # Direct recommendation request
    if any(word in message for word in ["suggest","recommend","eat","food","dish"]):
        food = recommend_food(selected_cuisine)
        return jsonify({"reply": food})

    if "anything" in message or "whatever" in message or "surprise" in message:
    
        if not user_data["diet"]:
            user_data["diet"] = random.choice(["veg","non veg"])

        if not user_data["spice"]:
            user_data["spice"] = random.choice(["spicy","mild"])

        if not user_data["meal"]:
            user_data["meal"] = random.choice(["breakfast","lunch","dinner"])

        if not user_data["goal"]:
            user_data["goal"] = "normal"

    ALLERGIES = ["milk","egg","eggs","fish","soy","nuts"]

    for allergy in ALLERGIES:
        if allergy in message and ("allergic" in message or "avoid" in message or "no " + allergy in message):

            # normalize plural
            if allergy == "eggs":
                allergy = "egg"

            user_data["allergy"] = allergy

            return jsonify({
                "reply": f"⚠️ Noted! I will avoid foods containing {allergy}."
            })
        
    DISLIKE_WORDS = ["don't like", "do not like", "i hate", "I hate", "avoid"]

    for phrase in DISLIKE_WORDS:
        if phrase in message:
            food = message.split(phrase)[-1].strip()

            if food not in user_data["dislikes"]:
                user_data["dislikes"].append(food)

            return jsonify({
                "reply": f"👍 Got it! I'll avoid {food} in future recommendations."
            })
        
    # Ask missing info
    if user_data["diet"] == "" and "veg" not in message and "non" not in message:
        return jsonify({"reply": "Are you Veg or Non-Veg?"})

    if user_data["spice"] == "":
        return jsonify({"reply": "Do you prefer Spicy 🌶️ or Mild food?"})

    if not user_data.get("meal"):
        return jsonify({"reply": "Which meal? Breakfast / Lunch / Dinner 🍽️"})

    if not user_data.get("goal"):
        return jsonify({
            "reply": "What is your health goal? Weight Loss 🥗 / Muscle Gain 💪 / Normal 🙂"
        })
    
    #if user_data.get("allergy"):
        return jsonify({
            "reply": f"⚠️ Thanks for telling me. I will avoid {user_data['allergy']}-based dishes in my recommendations."
        })
    
   

    # 🎯 Recommend food
    if user_data["diet"] and user_data["spice"] and user_data["meal"]:
        food = recommend_food(selected_cuisine)
    
    # Reset conversation (except name)
    user_data["diet"] = ""
    user_data["spice"] = ""
    user_data["meal"] = ""
    user_data["goal"] = ""

    return jsonify({"reply": food})

def score_food(food, goal):
    score = 0

    if goal == "Weight Loss":
        # prefer low calorie and high protein
        score += (food.protein * 2)
        score -= (food.calories / 50)

    elif goal == "Muscle Gain":
        # prefer high protein and higher calories
        score += (food.protein * 3)
        score += (food.calories / 100)

    else:  # Normal
        score += food.protein

    return score

def recommend_food(selected_cuisine=None):

    session = Session()

    try:
        query = session.query(Food)

        if user_data.get("allergy"):
            query = query.filter(Food.allergens != user_data["allergy"])

        if user_data.get("diet"):
            query = query.filter_by(diet=user_data["diet"])

        if user_data.get("spice"):
            query = query.filter_by(spice=user_data["spice"])

        if user_data.get("meal"):
            query = query.filter_by(meal=user_data["meal"])

        if selected_cuisine:
            query = query.filter_by(cuisine=selected_cuisine)

        foods = query.all()

        # remove disliked foods
        if user_data["dislikes"]:
            foods = [
                f for f in foods
                if not any(d in f.name.lower() for d in user_data["dislikes"])
            ]
        

        # fallback if cuisine filter returns nothing
        if not foods and selected_cuisine:

            query = session.query(Food)

            if user_data.get("diet"):
                query = query.filter_by(diet=user_data["diet"])

            if user_data.get("spice"):
                query = query.filter_by(spice=user_data["spice"])

            if user_data.get("meal"):
                query = query.filter_by(meal=user_data["meal"])

            foods = query.all()


        if not foods:
            return "😔 No matching food found."

        # -------- GOAL BASED SELECTION --------

        if user_data.get("goal") == "weight loss":

            low_calorie_foods = [f for f in foods if f.calories <= 400]

            if low_calorie_foods:
                selected_food = max(
                    low_calorie_foods,
                    key=lambda x: x.protein / x.calories
                )
            else:
                selected_food = max(
                    foods,
                    key=lambda x: x.protein / x.calories
                )

        elif user_data.get("goal") == "muscle gain":

            high_calorie_foods = [f for f in foods if f.calories >= 400]

            if high_calorie_foods:
                selected_food = max(
                    high_calorie_foods,
                    key=lambda x: (x.protein*3) + (x.calories/100)
                )
            else:
                selected_food = max(
                    foods,
                    key=lambda x: (x.protein*3) + (x.calories/100)
                )

        else:
            selected_food = random.choice(foods)

        global last_food
        global last_plan
        last_plan=""
        last_food = f"""
            Food: {selected_food.name}
            Calories: {selected_food.calories}
            Protein: {selected_food.protein}
            Cuisine: {selected_food.cuisine}
            """

        # -------- RESPONSE --------

        note = ""
        if not selected_cuisine:
            note = " (Chef's special recommendation 😊)"

        goal = user_data.get("goal","normal")

        result = (
            f"\n🎯 Goal: {goal.title()}\n"
            f"🍽️ Try {selected_food.name}{note}\n"
            f"Cuisine: {selected_food.cuisine.title()}\n"
            f"Calories: {selected_food.calories} kcal\n"
            f"Protein: {selected_food.protein} g"
        )

        nutrition_tracker["calories"] += selected_food.calories
        nutrition_tracker["protein"] += selected_food.protein
        

        return result

    finally:
        session.close()

#diet plan generator
def generate_diet_plan():

    global nutrition_tracker

    meals = ["breakfast","lunch","dinner"]

    session = Session()
    plan = []

    total_cal = 0
    total_protein = 0

    for meal in meals:

        query = session.query(Food)

        if user_data.get("diet"):
            query = query.filter_by(diet=user_data["diet"])

        if user_data.get("spice"):
            query = query.filter_by(spice=user_data["spice"])

        query = query.filter_by(meal=meal)

        foods = query.all()

        if not foods:
            continue

        food = random.choice(foods)

        total_cal += food.calories
        total_protein += food.protein

        nutrition_tracker["calories"] += food.calories
        nutrition_tracker["protein"] += food.protein

        plan.append((meal,food))

    session.close()

    result = "📅 **Your Daily Diet Plan**\n\n"

    for meal,food in plan:

        result += (
            f"🍽 {meal.title()}: {food.name}\n"
            f"Calories: {food.calories} kcal | Protein: {food.protein} g\n\n"
        )

    result += (
        f"🔥 Total Calories: {total_cal} kcal\n"
        f"💪 Total Protein: {total_protein} g"
    )

    global last_plan

    last_plan = ""
    for meal, food in plan:
        last_plan += f"""
            Food: {food.name}
            Calories: {food.calories}
            Protein: {food.protein}
            Cuisine: {food.cuisine}
            """
    print(len(last_plan))
        
    return result

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
client = InferenceClient(
    model="Qwen/Qwen2.5-7B-Instruct",
    token=HUGGINGFACE_API_KEY
)

def ai_food_chat(user_message, food_context):

    if food_context.count("Food:")>=2:
        prompt = f"""
        You are a friendly AI nutritionist.

        Here is a user's daily meal plan:

        {food_context}

        User question:
        {user_message}

        Explain in 2-3 sentences:
        • why this meal plan is healthy
        • how the foods complement each other
        • how the calories and protein support the user's goal

        Focus on the overall plan, not just one food.
        Keep it simple and friendly.
        """
                
        
    else:
        prompt = f"""
        You are a friendly AI nutritionist.

        Food or diet plan information:
        {food_context}

        User question:
        {user_message}

        Explain clearly in 2–3 sentences:
        • why this food is healthy
        • its nutrition benefits
        • how it helps the user’s health goal

        write only 2-3 sentences.
        Keep the explanation simple and friendly.
        """

    try:

        response = client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful nutrition expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        print("AI ERROR:", e)

        return "This food is nutritious and beneficial for your health."
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
