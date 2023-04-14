import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai

API_KEY = 'sk-' ####### 키

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



# 한글 깨짐없이 데이터 불러오기
df = pd.read_csv('data/food_list.csv',encoding='cp949')

# 입력될 데이터 추가
data_to_insert = {'구분': 'null', '음식명': 'null', '음식설명': 'null'}
df = df.append(data_to_insert, ignore_index=True)

# 필요한 데이터만 가져오기
data = df[['구분', '음식명', '음식설명']]

# 음식 설명 빈 줄 -> 거르기 #########################################

# 한글자 오류 방지하기 위해 데이터처리
for i in range (len(data)): # ,가 포함되거나 한 글자인 카테고리명 변경 / 문자가 있거나 한 글자인 음식명 변경
	if (',' in data['구분'][i]):
		data.loc[i, "구분"] = data['구분'][i].replace(',', '_')

	if (len(data['구분'][i]) == 1):
		data.loc[i, "구분"] = data['구분'][i] + "_"

	if (len(data['음식명'][i]) == 1):
		data.loc[i, "음식명"] = data['음식명'][i] + "_"

	if (" / " in data['음식명'][i]):
		data.loc[i, "음식명"] = data['음식명'][i].replace(" / ", '_')
	
	if ("/" in data['음식명'][i]):
		data.loc[i, "음식명"] = data['음식명'][i].replace("/", '_')

# 카테고리 벡터화
cv = CountVectorizer(ngram_range=(1,2)) 
cv_category = cv.fit_transform(data['구분']) 

def recommend_sim_cat(data):
	# 구분 벡터화
	cv_category = cv.fit_transform(data['구분']) 
	# print(cv.vocabulary_) # 카테고리별 인덱스 번호 

	# 코사인 유사도:구분
	similarity_category = cosine_similarity(cv_category, cv_category)
	sim_category = similarity_category.argsort()[:,::-1]
	# print(sim_category)
	# sim_category.shape
	return similarity_category


# 코사인 유사도:메뉴명
def recommend_sim_menu(data):
	cv_menuname = cv.fit_transform(data['음식명'])
	similarity_menuname = cosine_similarity(cv_menuname, cv_menuname)
	# sim_menuname = similarity_menuname.argsort()[:,::-1]
	return (similarity_menuname)
	# sim_menuname.shape

def recommend_sim(df):

	similarity_category = recommend_sim_cat(df)
	similarity_menuname = recommend_sim_menu(df)

	cate_menu_co = (
		+ similarity_category * 0.8
		+ similarity_menuname * 0.2
	)

	cate_menu_co_idx = cate_menu_co.argsort()[:,::-1]
	return (cate_menu_co_idx)


# 언더바 제거
def remove_in_list(menu_list):
	for i in range (len(menu_list)):
		menu_list[i] = menu_list[i].replace('_', '')
	return menu_list


def add_(str):
	if (len(str) == 1):
		str += "_"
	return str


# 추천 함수 (수정 중)
def recommend_menu(df, menu_name, top=7):

	last = len(df) - 1
	df.loc[last, "음식명"] = menu_name

	chat_res = callChatGPT(menu_name + " 는 [밥], [국], [면], [분식] 중에 뭐야")
	chat_res = add_(chat_res[chat_res.find('[')+1:chat_res.find(']')])


	# 질문 - 카테고리 다 뽑아오기 #########################################

	df.loc[last, "구분"] = chat_res # GPT 답변 : 메뉴 카테고리
	df.loc[last, "음식설명"] = callChatGPT(menu_name + " 영어 한줄 설명") # GPT 답변 : 메뉴 설명


	if (df.loc[last, "구분"] == "없는메뉴"):
		return ([])

	sorted_idx = recommend_sim(df)

	sim_idx = sorted_idx[[last], :top].reshape(-1)

	result = df.iloc[sim_idx]
	return result['음식명'].values ## 추천 메뉴 전송 필요



menu_name = "라면" ## 입력

lst = []

menu_name = add_(menu_name)

if (True in (data['음식명'] == menu_name).values): # 입력과 일치하는 메뉴가 있는 경우
		print("일치하는 메뉴가 있습니다.")
		lst.append(menu_name)
		
else : # 입력과 일치하는 메뉴명이 없는 경우
	lst = recommend_menu(data, menu_name)
	if (len(lst) != 0):
		print("일치하는 메뉴가 없습니다. 추천 메뉴는 다음과 같습니다.")

if (len(lst) == 0):
	print("메뉴가 없습니다.")
else :
	lst = remove_in_list(lst)
	print(lst) ## 주문 메뉴 전송 필요