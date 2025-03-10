import random

#LLM generated
adjectives = [
    "Martial", "Scitech", "Cosmic", "Aero", "Ultra", "Mega", "Hyper", "Quantum", 
    "Mystic", "Dynamic", "Sleek", "Rugged", "Vanguard", "Stealth", "Ethereal", 
    "Radical", "Rebel", "Futuristic", "Luminous", "Sonic"
]

roles = [
    "Artist", "Engineer", "Pilot", "Runner", "Warrior", "Architect", "Innovator", 
    "Inventor", "Technician", "Visionary", "Builder", "Creator", "Craftsman", 
    "Specialist", "Strategist", "Designer"
]

specialties = [
    "Free Runner", "Fauji", "Cosplay", "Scifi", "Martial Artist", "Stunts Artist",
    "Wood Worker", "Cyber Warrior", "Space Ranger", "Tech Savvy", "Battle Master"
]

versions = set()

# Create a mix by combining 2 to 3 elements (either adjectives, roles, or specialties)
while len(versions) < 200:
    parts = []
    structure_type = random.choice([1, 2, 3])
    if structure_type == 1:
        parts.append(random.choice(specialties))
        parts.append(random.choice(specialties))
    elif structure_type == 2:
        parts.append(random.choice(adjectives))
        parts.append(random.choice(roles))
        parts.append(random.choice(specialties))
    else:
        parts.append(random.choice(adjectives))
        parts.append(random.choice(roles))
    version_name = "+".join(parts)
    versions.add(version_name)

versions_list = list(versions)
print("Total versions generated:", len(versions_list))

product_types = [
    "Flying Car", "Hoverboard", "Jetpack", "Rocket Skateboard", "Hyper Bike", "Smart Drone",
    "Anti-Gravity Suit", "Solar-Powered Glider", "Neon Bike", "Autonomous Truck"
]

product_adjectives = [
    "Ultra-lightweight", "Advanced", "Eco-friendly", "Solar-powered", "Autonomous", 
    "High-speed", "Futuristic", "Quantum", "Next-Gen", "Revolutionary"
]

unique_features = [
    "3000cc", "400HP", "2.5m x 1.8m", "4-seater", "10-speed", "Turbocharged", 
    "Limited Edition", "Stealth Mode", "All-Terrain", "Hyper Mode"
]

# Generate 150 unique product titles
product_titles = set()
while len(product_titles) < 150:
    prod_type = random.choice(product_types)
    adjective = random.choice(product_adjectives)
    feature = random.choice(unique_features)
    
    title = f"{adjective} {prod_type} ({feature})"
    product_titles.add(title)

product_titles_list = list(product_titles)
print("Total product titles generated:", len(product_titles_list))

