# Python script for ChatGPT-based AI Chatbot for code completion

# Import necessary libraries
import openai

# Set up OpenAI API key
api_key = "YOUR_API_KEY"
openai.api_key = api_key

# Define function for ChatGPT code completion
def complete_code(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text

# Main function to interact with the chatbot
def chatbot():
    print("Welcome to the ChatGPT Code Completion Chatbot!")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break
        prompt = f"Code: {user_input}\nCompletion:"
        completion = complete_code(prompt)
        print("Chatbot:", completion)

# Run the chatbot
if __name__ == "__main__":
    chatbot()

