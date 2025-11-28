# chat bot for general query

# Chatbot.py

from google import genai
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GeminiAPIKey = env_vars.get("GeminiAPIKey")

# Initialize Gemini client
client = genai.Client(api_key=GeminiAPIKey)

# System instruction
SystemPrompt = f"""
Hello, I am {Username}. You are an accurate and advanced AI chatbot named {Assistantname}.
*** Do not tell time until asked. ***
*** Reply ONLY in English, even if user speaks Hindi. ***
*** Never mention training data. ***
*** Answer clearly, shortly, without unnecessary text. ***
"""


# ⏳ Real-time information
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        "Use this real-time information if necessary:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%I')} hours : {now.strftime('%M')} minutes : {now.strftime('%S')} seconds.\n"
    )


# Clean AI output
def AnswerModifier(text):
    lines = text.split("\n")
    non_empty = [line.strip() for line in lines if line.strip()]
    return "\n".join(non_empty)


# 🤖 MAIN CHATBOT FUNCTION
def ChatBot(Query):

    try:
        # Load existing log
        try:
            with open(r"Data/ChatLog.json", "r") as f:
                messages = load(f)
        except FileNotFoundError:
            messages = []

        # Add user message
        messages.append({"role": "user", "content": Query})

        # -------------------------------
        # 🔥 CONVERT MESSAGES FOR GEMINI
        # -------------------------------
        gemini_messages = []

        # System prompt added as "user" role
        gemini_messages.append({
            "role": "user",
            "parts": [{"text": SystemPrompt}]
        })

        # Real-time info also as user role
        gemini_messages.append({
            "role": "user",
            "parts": [{"text": RealtimeInformation()}]
        })

        # Convert stored messages to valid Gemini roles
        for msg in messages:
            # Gemini only accepts "user" and "model"
            role = "user" if msg["role"] == "user" else "model"

            gemini_messages.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        # --------------------------------------
        # 🔥 SEND REQUEST TO GEMINI (STREAMING)
        # --------------------------------------
        completion = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=gemini_messages,
            
        )

        Answer = ""

        # Streaming output
        for chunk in completion:
            if hasattr(chunk, "text") and chunk.text:
                Answer += chunk.text

        Answer = Answer.replace("</s>", "")

        # Add model reply to the log
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat log
        with open(r"Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print("Error:", e)

        # Reset log if something breaks
        with open(r"Data/ChatLog.json", "w") as f:
            dump([], f)

        return "An error occurred. I reset the conversation."


# ---------------------------
# RUN LOOP (ONLY FOR TESTING)
# ---------------------------
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        print("Jarvis:", ChatBot(user_input))
