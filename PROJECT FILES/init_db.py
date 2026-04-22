from backend.models import Base, Food
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create engine for SQLite database
engine = create_engine('sqlite:///food.db', echo=False)

# Create tables
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# -------------------- FOOD DATASET --------------------

foods_data = [

# ==================== BREAKFAST ====================

# Veg Mild
{"name":"Idli with Sambar","diet":"veg","spice":"mild","meal":"breakfast","cuisine":"south indian","calories":220,"protein":8,"allergens":"none"},
{"name":"Oats Porridge","diet":"veg","spice":"mild","meal":"breakfast","cuisine":"continental","calories":250,"protein":9,"allergens":"none"},
{"name":"Vegetable Upma","diet":"veg","spice":"mild","meal":"breakfast","cuisine":"south indian","calories":300,"protein":7,"allergens":"none"},
{"name":"Greek Yogurt Fruit Bowl","diet":"veg","spice":"mild","meal":"breakfast","cuisine":"continental","calories":220,"protein":15,"allergens":"milk"},

# Veg Spicy
{"name":"Podi Dosa","diet":"veg","spice":"spicy","meal":"breakfast","cuisine":"south indian","calories":320,"protein":8,"allergens":"none"},
{"name":"Paneer Stuffed Paratha","diet":"veg","spice":"spicy","meal":"breakfast","cuisine":"north indian","calories":480,"protein":18,"allergens":"milk"},

# Non Veg Mild
{"name":"Boiled Eggs (2)","diet":"non veg","spice":"mild","meal":"breakfast","cuisine":"continental","calories":160,"protein":13,"allergens":"egg"},
{"name":"Egg White Omelette","diet":"non veg","spice":"mild","meal":"breakfast","cuisine":"continental","calories":200,"protein":18,"allergens":"egg"},

# Non Veg Spicy
{"name":"Masala Omelette","diet":"non veg","spice":"spicy","meal":"breakfast","cuisine":"indian","calories":350,"protein":20,"allergens":"egg"},
{"name":"Chicken Breakfast Wrap","diet":"non veg","spice":"spicy","meal":"breakfast","cuisine":"american","calories":500,"protein":28,"allergens":"none"},


# ==================== LUNCH ====================

# Veg Mild
{"name":"Dal Khichdi","diet":"veg","spice":"mild","meal":"lunch","cuisine":"indian","calories":330,"protein":11,"allergens":"none"},
{"name":"Vegetable Stew","diet":"veg","spice":"mild","meal":"lunch","cuisine":"south indian","calories":280,"protein":6,"allergens":"none"},
{"name":"Tofu Salad Bowl","diet":"veg","spice":"mild","meal":"lunch","cuisine":"continental","calories":260,"protein":14,"allergens":"soy"},
{"name":"Chickpea Protein Bowl","diet":"veg","spice":"mild","meal":"lunch","cuisine":"continental","calories":390,"protein":20,"allergens":"none"},

# Veg Spicy
{"name":"Veg Biryani","diet":"veg","spice":"spicy","meal":"lunch","cuisine":"indian","calories":450,"protein":10,"allergens":"none"},
{"name":"Paneer Tikka","diet":"veg","spice":"spicy","meal":"lunch","cuisine":"north indian","calories":500,"protein":22,"allergens":"milk"},
{"name":"Soya Chunk Curry","diet":"veg","spice":"spicy","meal":"lunch","cuisine":"indian","calories":520,"protein":28,"allergens":"soy"},

# Non Veg Mild
{"name":"Grilled Chicken Breast","diet":"non veg","spice":"mild","meal":"lunch","cuisine":"american","calories":380,"protein":35,"allergens":"none"},
{"name":"Fish Curry (Light)","diet":"non veg","spice":"mild","meal":"lunch","cuisine":"south indian","calories":420,"protein":30,"allergens":"fish"},

# Non Veg Spicy
{"name":"Chicken Chettinad","diet":"non veg","spice":"spicy","meal":"lunch","cuisine":"south indian","calories":550,"protein":32,"allergens":"none"},
{"name":"Mutton Curry","diet":"non veg","spice":"spicy","meal":"lunch","cuisine":"indian","calories":650,"protein":38,"allergens":"none"},


# ==================== DINNER ====================

# Veg Mild
{"name":"Clear Vegetable Soup","diet":"veg","spice":"mild","meal":"dinner","cuisine":"continental","calories":180,"protein":5,"allergens":"none"},
{"name":"Sprouts Salad","diet":"veg","spice":"mild","meal":"dinner","cuisine":"indian","calories":240,"protein":12,"allergens":"none"},
{"name":"Millet Khichdi","diet":"veg","spice":"mild","meal":"dinner","cuisine":"indian","calories":320,"protein":10,"allergens":"none"},

# Veg Spicy
{"name":"Kadai Paneer","diet":"veg","spice":"spicy","meal":"dinner","cuisine":"indian","calories":520,"protein":20,"allergens":"milk"},
{"name":"Tofu Stir Fry","diet":"veg","spice":"spicy","meal":"dinner","cuisine":"continental","calories":420,"protein":21,"allergens":"soy"},
{"name":"Spicy Mushroom Masala","diet":"veg","spice":"spicy","meal":"dinner","cuisine":"indian","calories":380,"protein":12,"allergens":"none"},
{"name":"Paneer Bhurji","diet":"veg","spice":"spicy","meal":"dinner","cuisine":"indian","calories":480,"protein":24,"allergens":"milk"},

# Non Veg Mild
{"name":"Grilled Fish","diet":"non veg","spice":"mild","meal":"dinner","cuisine":"continental","calories":350,"protein":32,"allergens":"fish"},
{"name":"Chicken Stew","diet":"non veg","spice":"mild","meal":"dinner","cuisine":"south indian","calories":400,"protein":28,"allergens":"none"},

# Non Veg Spicy
{"name":"Pepper Mutton","diet":"non veg","spice":"spicy","meal":"dinner","cuisine":"south indian","calories":680,"protein":40,"allergens":"none"},
{"name":"Spicy Chicken Roast","diet":"non veg","spice":"spicy","meal":"dinner","cuisine":"indian","calories":520,"protein":34,"allergens":"none"},
{"name":"Butter Chicken","diet":"non veg","spice":"spicy","meal":"dinner","cuisine":"north indian","calories":600,"protein":30,"allergens":"milk"}

]



# -------------------- INSERT INTO DATABASE --------------------

for food in foods_data:
    new_food = Food(**food)
    session.add(new_food)

session.commit()
session.close()

print("✅ Database created successfully with SQLAlchemy!")