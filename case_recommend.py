import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# 한글 깨짐없이 데이터 불러오기
df = pd.read_csv('food_list.csv',encoding='cp949')

# 입력될 데이터 추가
data_to_insert = {'구분': '_', '음식명': '_'}
df = df.append(data_to_insert, ignore_index=True)

# 필요한 데이터만 가져오기
data = df[['구분', '음식명']] 

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


def menu_cat(menu_name, df):
	menu_list = []
	menu_cat = "없는메뉴"

	lst = []

	for key, val in cv.vocabulary_.items():
		menu_list.append(key)

	remove_in_list(menu_list)

	for key in menu_list:
		if key in menu_name:
			if (len(key) == 1):
				key = key + "_"
				print(key)
				return key
			if ("_" in key):
				lst.append(key)
				print(lst)
	
	return menu_cat

# 추천 함수 (수정 중)
def recommend_menu_(df, menu_name, top=7):

	lst = []

	for i in range (len(data)):
		lst.append(menu_name in df['음식명'][i])

	if True in lst:
		result = df.iloc[lst]
		return result['음식명'].values ## 추천 메뉴 전송 필요


	last = len(df) - 1
	df.loc[last, "음식명"] = menu_name
	df.loc[last, "구분"] = menu_cat(menu_name, df)
	print(menu_cat(menu_name, df))

	sorted_idx = recommend_sim(df)

	
	#print(sorted_idx)

	sim_idx = sorted_idx[[last], :top].reshape(-1)
	#print(sim_idx)

	result = df.iloc[sim_idx]
	return result['음식명'].values ## 추천 메뉴 전송 필요



# 입력
"""
menu_name = "미역국"

if (len(menu_name) == 1):
	menu_name += "_"

print(recommend_menu_(data, menu_name))
"""

#"""
menu_name = "겨자" ## 입력

lst = []

if (len(menu_name) == 1):
	menu_name += "_"

if (True in (data['음식명'] == menu_name).values): # 입력과 일치하는 메뉴가 있는 경우
		print("일치하는 메뉴가 있습니다.")
		lst.append(menu_name)
		
else : # 입력과 일치하는 메뉴명이 없는 경우
	lst = recommend_menu_(data, menu_name)
	if (len(lst) != 0):
		print("일치하는 메뉴가 없습니다. 추천 메뉴는 다음과 같습니다.")

if (len(lst) == 0):
	print("메뉴가 없습니다.")
else :
	lst = remove_in_list(lst)
	print(lst) ## 주문 메뉴 전송 필요

#"""
