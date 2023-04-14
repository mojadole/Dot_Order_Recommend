import openai

API_KEY = 'sk-' ## 키

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

menu = "라면"

print(callChatGPT(menu + " 영어 한줄 설명"))
print()

res = callChatGPT(menu + " 는 [밥], [국], [면], [분식] 중에 뭐야")

res = res[res.find('[')+1:res.find(']')]
print(res)