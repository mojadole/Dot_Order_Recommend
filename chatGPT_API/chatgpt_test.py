import openai

API_KEY = #''

def callChatGPT(prompt, API_KEY=API_KEY):
    
    messages = []

    #get api key
    openai.api_key = API_KEY

    messages.append({"role":"user", "content":prompt})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    chat_response = completion.choices[0].message.content
    messages.append({"role":"assitant", "content":chat_response})

    return messages[1]["content"]

prompt = input("Inser a prompt: ")
print(callChatGPT(prompt))