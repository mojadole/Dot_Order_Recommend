import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

df = pd.read_csv('food_list.csv',encoding='cp949')
#category = df['구분']
#name = print(df['음식명'])

data = df[['구분', '음식명']]

print(data)

counter_vector = CountVectorizer(ngram_range=(1,1))
c_v_category = counter_vector.fit_transform(data['구분'])
c_v_category.shape