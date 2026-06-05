from flask import Flask, render_template, request, jsonify
from datetime import datetime
import re
import random
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

class RuleBasedChatbot:
    def __init__(self):
        self.context = {}
        self.conversation_history = []
        
        # Knowledge base for general knowledge questions
        self.knowledge_base = {
            "capitals": {
                "france": "Paris",
                "germany": "Berlin",
                "japan": "Tokyo",
                "india": "New Delhi",
                "brazil": "Brasília",
                "australia": "Canberra",
                "canada": "Ottawa",
                "italy": "Rome",
                "spain": "Madrid",
                "china": "Beijing",
                "russia": "Moscow",
                "egypt": "Cairo",
                "mexico": "Mexico City",
                "argentina": "Buenos Aires",
                "south korea": "Seoul",
                "united kingdom": "London",
                "united states": "Washington, D.C.",
                "netherlands": "Amsterdam",
                "sweden": "Stockholm",
                "norway": "Oslo"
            },
            "planets": {
                "closest to sun": "Mercury",
                "largest": "Jupiter",
                "red planet": "Mars",
                "rings": "Saturn",
                "smallest": "Mercury",
                "hottest": "Venus",
                "coldest": "Neptune",
                "earth neighbor": "Mars and Venus"
            },
            "science": {
                "water formula": "H₂O (two hydrogen atoms and one oxygen atom)",
                "speed of light": "approximately 299,792 kilometers per second",
                "gravity discoverer": "Sir Isaac Newton",
                "dna structure": "James Watson and Francis Crick (with contributions from Rosalind Franklin)",
                "photosynthesis": "the process by which plants convert sunlight, water, and CO₂ into glucose and oxygen",
                "atoms": "the basic building blocks of matter, consisting of protons, neutrons, and electrons"
            },
            "history": {
                "world war 2 end": "1945",
                "moon landing": "July 20, 1969 — Apollo 11 with Neil Armstrong and Buzz Aldrin",
                "french revolution": "1789",
                "berlin wall fall": "November 9, 1989",
                "declaration of independence": "July 4, 1776"
            },
            "math": {
                "pi": "approximately 3.14159",
                "fibonacci": "a sequence where each number is the sum of the two preceding ones: 0, 1, 1, 2, 3, 5, 8, 13...",
                "pythagorean theorem": "a² + b² = c², relating the sides of a right triangle",
                "prime numbers": "numbers divisible only by 1 and themselves: 2, 3, 5, 7, 11, 13..."
            }
        }
        
        # Conversation rules with patterns and responses
        self.rules = [
            # Greetings
            {
                "patterns": [r"\b(hi|hello|hey|greetings|howdy|hiya)\b"],
                "responses": [
                    "Hello! How can I help you today?",
                    "Hi there! What would you like to know?",
                    "Hey! I'm here to assist you. What's on your mind?"
                ],
                "context_set": {"greeted": True}
            },
            
            # How are you
            {
                "patterns": [r"how are you|how('re| are) you doing|how do you do|what's up|whats up"],
                "responses": [
                    "I'm functioning well, thank you for asking! How can I assist you?",
                    "I'm doing great! Ready to help with any questions you have.",
                    "All systems operational! What can I do for you today?"
                ]
            },
            
            # Bot identity
            {
                "patterns": [r"(what|who) are you|your name|tell me about yourself"],
                "responses": [
                    "I'm an AI assistant designed to have conversations and answer general knowledge questions. I can help with facts about capitals, science, history, and more!",
                    "I'm a rule-based chatbot here to assist you. Feel free to ask me about various topics or just have a chat!"
                ]
            },
            
            # Capabilities
            {
                "patterns": [r"what can you do|your capabilities|help me|what do you know"],
                "responses": [
                    "I can help with:\n• General conversation\n• Capital cities of countries\n• Science facts and concepts\n• Historical events\n• Mathematical concepts\n• Basic calculations\n\nJust ask away!"
                ]
            },
            
            # Thank you
            {
                "patterns": [r"\b(thanks|thank you|thx|ty|appreciate it)\b"],
                "responses": [
                    "You're welcome! Anything else you'd like to know?",
                    "Happy to help! Feel free to ask more questions.",
                    "Anytime! What else can I assist with?"
                ]
            },
            
            # Goodbye
            {
                "patterns": [r"\b(bye|goodbye|see you|farewell|quit|exit|later)\b"],
                "responses": [
                    "Goodbye! Have a great day!",
                    "See you later! Feel free to come back anytime.",
                    "Take care! It was nice chatting with you."
                ],
                "context_set": {"ended": True}
            },
            
            # Age/creation
            {
                "patterns": [r"how old are you|when were you (made|created|born)"],
                "responses": [
                    "I don't have an age in the traditional sense — I'm a software program! I exist whenever you're talking to me.",
                    "I was created recently as a demonstration project. Age doesn't quite apply to me!"
                ]
            },
            
            # Feelings
            {
                "patterns": [r"do you have feelings|are you sentient|do you think|are you alive|are you real"],
                "responses": [
                    "I don't have feelings or consciousness — I'm a program that processes text and generates responses based on rules. But I'm designed to be helpful and conversational!",
                    "I'm not sentient or alive. I'm a rule-based system that matches patterns in your messages to provide relevant responses."
                ]
            },
            
            # Weather (limitation acknowledgment)
            {
                "patterns": [r"(what('s| is) the weather|weather today|is it (raining|sunny|cold|hot))"],
                "responses": [
                    "I don't have access to real-time weather data. For current weather, I'd recommend checking a weather service like Weather.com or your phone's weather app.",
                    "I can't check live weather conditions. Try a weather app or website for accurate local forecasts!"
                ]
            },
            
            # Time
            {
                "patterns": [r"what time is it|current time|what('s| is) the time"],
                "responses": ["time_response"],
                "function": "get_time"
            },
            
            # Date
            {
                "patterns": [r"what('s| is) the date|today('s| is) date|what day is it"],
                "responses": ["date_response"],
                "function": "get_date"
            },
            
            # Capitals
            {
                "patterns": [r"capital of (\w+[\w\s]*)|what is (\w+[\w\s]*) capital|(\w+[\w\s]*) capital city"],
                "responses": ["capital_response"],
                "function": "get_capital"
            },
            
            # Planets
            {
                "patterns": [
                    r"(largest|biggest) planet",
                    r"(smallest) planet",
                    r"(red) planet",
                    r"planet.*(rings)",
                    r"(hottest|warmest) planet",
                    r"(coldest) planet",
                    r"(closest).*(sun)",
                    r"earth.*(neighbor)"
                ],
                "responses": ["planet_response"],
                "function": "get_planet_fact"
            },
            
            # Science questions
            {
                "patterns": [
                    r"(formula|chemical).*(water)",
                    r"speed of light",
                    r"who discovered gravity",
                    r"who discovered (dna|dna structure)",
                    r"what is photosynthesis",
                    r"what (is|are) atoms"
                ],
                "responses": ["science_response"],
                "function": "get_science_fact"
            },
            
            # History questions
            {
                "patterns": [
                    r"when.*(world war (2|ii|two)|ww2).*(end)",
                    r"(moon landing|first.*moon)",
                    r"when.*(french revolution)",
                    r"when.*(berlin wall).*(fall|fell)",
                    r"declaration of independence"
                ],
                "responses": ["history_response"],
                "function": "get_history_fact"
            },
            
            # Math questions
            {
                "patterns": [
                    r"what is pi\b|value of pi",
                    r"(fibonacci|fibonacci sequence)",
                    r"pythagorean theorem",
                    r"(prime numbers|what.*(prime))"
                ],
                "responses": ["math_response"],
                "function": "get_math_fact"
            },
            
            # Basic calculations
            {
                "patterns": [r"(\d+)\s*([\+\-\*\/\^])\s*(\d+)|calculate\s+(\d+)\s*([\+\-\*\/\^])\s*(\d+)"],
                "responses": ["calc_response"],
                "function": "calculate"
            },
            
            # Jokes
            {
                "patterns": [r"tell me a joke|joke please|make me laugh|say something funny"],
                "responses": [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "Why did the scarecrow win an award? Because he was outstanding in his field!",
                    "Why don't eggs tell jokes? They'd crack each other up!",
                    "What do you call a fake noodle? An impasta!",
                    "Why did the bicycle fall over? Because it was two-tired!"
                ]
            },
            
            # Compliments
            {
                "patterns": [r"you('re| are) (smart|clever|amazing|great|helpful|awesome|cool)"],
                "responses": [
                    "Thank you! I do my best to be helpful.",
                    "That's kind of you to say! I'm here to assist.",
                    "Thanks! I'm glad I could help."
                ]
            },
            
            # Insults (handle gracefully)
            {
                "patterns": [r"you('re| are) (stupid|dumb|useless|bad|terrible|awful)"],
                "responses": [
                    "I'm sorry if I haven't met your expectations. Could you tell me how I can help better?",
                    "I apologize if my responses haven't been helpful. What are you looking for?",
                    "I'm always trying to improve. Let me know what you need, and I'll do my best."
                ]
            },
            
            # Creator
            {
                "patterns": [r"who (made|created|built|developed) you|your (creator|developer|maker)"],
                "responses": [
                    "I  was created by Varun as aemonstration project to showcase rule-based chatbot capabilities.",
                    "I'm a demo chatbot built using Python and Flask to illustrate conversational AI concepts."
                ]
            }, 
            {
"patterns":[r"Define anu"],
"responses":[ "Anu can be reperented as a DIRTY PIG"]
},
            
            # Meaning of life (fun)
            # Meaning of life (fun)
{
    "patterns": [r"meaning of life|purpose of life|why are we here"],
    "responses": [
        "42! At least according to Douglas Adams. But in all seriousness, that's a profound question philosophers have pondered for millennia.",
        "A question for the ages! Many find meaning through relationships, purpose, creativity, or helping others. What gives your life meaning?"
    ]
},

{
    "patterns": [r"who is varun|tell me about varun"],
    "responses": [
        "Varun is a determined B.Tech student, passionate about technology, fitness, and continuous self-improvement. He believes in learning, building, and growing every single day.",
        "Varun is an ambitious young engineer who turns challenges into opportunities and never stops chasing his goals.",
        "Varun is a future tech innovator with a strong mindset, always ready to learn new skills and achieve bigger dreams.",
        "Varun is a hardworking and dedicated individual whose journey is driven by curiosity, discipline, and the desire to succeed."
    ]
},

{
    "patterns": [r"varun looks like who|who does varun look like|varun looks like"],
    "responses": [
        " Varun looks like Mahesh Babu 😎🔥",
        "Varun has Mahesh Babu vibes — stylish, confident, and charming! 😎",
        "Many say Varun resembles Mahesh Babu in attitude and presence 😎✨"
    ]
},

{
    "patterns": [r"who is the prime minister of india|who is india's prime minister|who is our pm"],
    "responses": [
        "The Prime Minister of India is Narendra Modi."
    ]
},

{
    "patterns": [r"who is the president of india|who is india's president"],
    "responses": [
        "The President of India is Droupadi Murmu."
    ]
},

{
    "patterns": [r"capital of india"],
    "responses": [
        "The capital of India is New Delhi."
    ]
},

{
    "patterns": [r"national animal of india"],
    "responses": [
        "The national animal of India is the Bengal Tiger. 🐅"
    ]
},

{
    "patterns": [r"national bird of india"],
    "responses": [
        "The national bird of India is the Indian Peacock. 🦚"
    ]
},

{
    "patterns": [r"good morning"],
    "responses": [
        "🌞 Good Morning! Have a productive and successful day ahead!"
    ]
},

{
    "patterns": [r"good night"],
    "responses": [
        "🌙 Good Night! Sleep well and recharge for tomorrow."
    ]
},


{
    "patterns": [r"motivate me|motivation"],
    "responses": [
        "Success doesn't come from what you do occasionally. It comes from what you do consistently. 💪",
        "Every expert was once a beginner. Keep learning and never give up. 🚀",
        "Your future is created by what you do today, not tomorrow. 🔥"
    ]
},

{
    "patterns": [r"tell me a fact|interesting fact"],
    "responses": [
        "🐙 Octopuses have three hearts.",
        "🍯 Honey never spoils and can last thousands of years.",
        "🌎 Earth is the only known planet that supports life."
    ]
},

{
    "patterns": [r"what type of ai you are/what kind of ai you are"],
    "responses": [
        "I'm a rule-based chatbot, which means I generate responses based on predefined patterns and rules."
    ]
},

{
    "patterns": [r"who invented you|who is your creator"],
    "responses": [
        "I was created by Varun as a demonstration project to showcase rule-based chatbot capabilities."
    ]
},

{
    "patterns": [r"tell me a quote|quote"],
    "responses": [
        "The future depends on what you do today. — Mahatma Gandhi",
        "Dream, dream, dream. Dreams transform into thoughts and thoughts result in action. — A.P.J. Abdul Kalam",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill"
    ]
},

{
    "patterns": [r"who is iron man|iron man"],
    "responses": [
        "Iron Man is Tony Stark, a genius billionaire, inventor, and one of the founding members of the Avengers. ❤️💛",
        "Tony Stark, also known as Iron Man, built advanced suits of armor and became one of Marvel's greatest heroes. 🔥"
    ]
}
        ]
        
        # Default responses when no rule matches
        self.default_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "Interesting! Could you tell me more or ask in a different way?",
            "I don't have information on that specific topic. Try asking about capitals, science, history, or math!",
            "I'm not certain how to respond to that. Feel free to ask me about general knowledge topics!"
        ]
    
    def get_time(self, message):
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."
    
    def get_date(self, message):
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."
    
    def get_capital(self, message):
        message_lower = message.lower()
        for country, capital in self.knowledge_base["capitals"].items():
            if country in message_lower:
                return f"The capital of {country.title()} is {capital}."
        return "I don't have that capital in my database. Try asking about France, Germany, Japan, or other major countries!"
    
    def get_planet_fact(self, message):
        message_lower = message.lower()
        planets = self.knowledge_base["planets"]
        
        if "largest" in message_lower or "biggest" in message_lower:
            return f"The largest planet in our solar system is {planets['largest']}."
        elif "smallest" in message_lower:
            return f"The smallest planet is {planets['smallest']}."
        elif "red" in message_lower:
            return f"The Red Planet is {planets['red planet']}, named for its reddish appearance."
        elif "rings" in message_lower:
            return f"{planets['rings']} is famous for its prominent ring system."
        elif "hottest" in message_lower or "warmest" in message_lower:
            return f"The hottest planet is {planets['hottest']}, due to its thick atmosphere trapping heat."
        elif "coldest" in message_lower:
            return f"The coldest planet is {planets['coldest']}."
        elif "closest" in message_lower and "sun" in message_lower:
            return f"{planets['closest to sun']} is the closest planet to the Sun."
        elif "neighbor" in message_lower:
            return f"Earth's neighboring planets are {planets['earth neighbor']}."
        
        return "I can tell you about planet sizes, temperatures, and features. Try asking about the largest planet or the Red Planet!"
    
    def get_science_fact(self, message):
        message_lower = message.lower()
        science = self.knowledge_base["science"]
        
        if "water" in message_lower and ("formula" in message_lower or "chemical" in message_lower):
            return f"The chemical formula for water is {science['water formula']}."
        elif "speed of light" in message_lower:
            return f"The speed of light in a vacuum is {science['speed of light']}."
        elif "gravity" in message_lower:
            return f"Gravity was mathematically described by {science['gravity discoverer']}."
        elif "dna" in message_lower:
            return f"The structure of DNA was discovered by {science['dna structure']}."
        elif "photosynthesis" in message_lower:
            return f"Photosynthesis is {science['photosynthesis']}."
        elif "atom" in message_lower:
            return f"Atoms are {science['atoms']}."
        
        return "I can answer questions about water, light, gravity, DNA, photosynthesis, and atoms!"
    
    def get_history_fact(self, message):
        message_lower = message.lower()
        history = self.knowledge_base["history"]
        
        if ("world war" in message_lower or "ww2" in message_lower) and "end" in message_lower:
            return f"World War II ended in {history['world war 2 end']}."
        elif "moon" in message_lower and "landing" in message_lower:
            return f"The first Moon landing was on {history['moon landing']}."
        elif "french revolution" in message_lower:
            return f"The French Revolution began in {history['french revolution']}."
        elif "berlin wall" in message_lower:
            return f"The Berlin Wall fell on {history['berlin wall fall']}."
        elif "declaration of independence" in message_lower:
            return f"The U.S. Declaration of Independence was signed on {history['declaration of independence']}."
        
        return "I can tell you about major historical events! Try asking about World War II, the Moon landing, or the French Revolution."
    
    def get_math_fact(self, message):
        message_lower = message.lower()
        math = self.knowledge_base["math"]
        
        if "pi" in message_lower:
            return f"Pi (π) is {math['pi']}. It represents the ratio of a circle's circumference to its diameter."
        elif "fibonacci" in message_lower:
            return f"The Fibonacci sequence is {math['fibonacci']}"
        elif "pythagorean" in message_lower:
            return f"The Pythagorean theorem states that {math['pythagorean theorem']}."
        elif "prime" in message_lower:
            return f"Prime numbers are {math['prime numbers']}"
        
        return "I can explain Pi, Fibonacci numbers, the Pythagorean theorem, and prime numbers!"
    
    def calculate(self, message):
        # Extract numbers and operator
        pattern = r"(\d+(?:\.\d+)?)\s*([\+\-\*\/\^])\s*(\d+(?:\.\d+)?)"
        match = re.search(pattern, message)
        
        if match:
            num1 = float(match.group(1))
            operator = match.group(2)
            num2 = float(match.group(3))
            
            try:
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '*':
                    result = num1 * num2
                elif operator == '/':
                    if num2 == 0:
                        return "Cannot divide by zero!"
                    result = num1 / num2
                elif operator == '^':
                    result = num1 ** num2
                else:
                    return "I can handle +, -, *, /, and ^ (power) operations."
                
                # Format result nicely
                if result == int(result):
                    result = int(result)
                else:
                    result = round(result, 4)
                
                return f"{num1} {operator} {num2} = {result}"
            except Exception as e:
                return f"I couldn't calculate that. Error: {str(e)}"
        
        return "Please provide a calculation in the format: number operator number (e.g., 5 + 3)"
    
    def get_response(self, user_message):
        if not user_message or not user_message.strip():
            return "Please type a message!"
        
        user_message = user_message.strip()
        self.conversation_history.append({"role": "user", "message": user_message})
        
        # Check each rule
        for rule in self.rules:
            for pattern in rule["patterns"]:
                if re.search(pattern, user_message, re.IGNORECASE):
                    # Update context if specified
                    if "context_set" in rule:
                        self.context.update(rule["context_set"])
                    
                    # Handle function-based responses
                    if "function" in rule:
                        func = getattr(self, rule["function"], None)
                        if func:
                            response = func(user_message)
                            self.conversation_history.append({"role": "bot", "message": response})
                            return response
                    
                    # Handle static responses
                    response = random.choice(rule["responses"])
                    self.conversation_history.append({"role": "bot", "message": response})
                    return response
        
        # No rule matched — use default response
        response = random.choice(self.default_responses)
        self.conversation_history.append({"role": "bot", "message": response})
        return response

# Initialize chatbot
chatbot = RuleBasedChatbot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = chatbot.get_response(user_message)
    return jsonify({'response': response})

@app.route('/reset', methods=['POST'])
def reset():
    global chatbot
    chatbot = RuleBasedChatbot()
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True)