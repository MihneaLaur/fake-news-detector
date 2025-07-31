import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np


fake_news = [
    "Breaking news: The president was replaced by a robot.",
    "Scientists discovered a new species of flying pigs.",
    "The moon is actually made of cheese, NASA confirms.",
    "Breaking: Aliens landed in New York City last night.",
    "New study proves that vaccines cause autism.",
    "The government is hiding the truth about COVID-19.",
    "Breaking: World War 3 has started in Europe.",
    "Scientists found a cure for all diseases.",
    "The stock market will crash tomorrow, insiders say.",
    "Breaking: The Earth is flat, new evidence shows."
]

real_news = [
    "Scientists discovered water on Mars.",
    "The stock market showed moderate growth today.",
    "New climate change report shows rising temperatures.",
    "Tech company announces new smartphone features.",
    "Local community raises funds for charity.",
    "Sports team wins championship after close game.",
    "New study shows benefits of regular exercise.",
    "City council approves new infrastructure project.",
    "Scientists develop new renewable energy technology.",
    "Education department announces new curriculum changes."
]

# Combinăm datele
texts = fake_news + real_news
labels = [1] * len(fake_news) + [0] * len(real_news)

# Creăm vectorizatorul cu mai multe opțiuni
vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 2)
)

# Antrenăm vectorizatorul și modelul
X = vectorizer.fit_transform(texts)
model = LogisticRegression(max_iter=1000)
model.fit(X, labels)

# Salvăm modelul și vectorizatorul
with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model antrenat și salvat cu succes!")
print(f"Număr de cuvinte în vocabular: {len(vectorizer.get_feature_names_out())}")
print(f"Acuratețe pe setul de antrenare: {model.score(X, labels):.2f}")
print(model.predict(vectorizer.transform(["Breaking news: The president was replaced by a robot."])))