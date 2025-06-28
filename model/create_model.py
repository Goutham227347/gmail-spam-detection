from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import os

os.makedirs("model", exist_ok=True)

texts = ["Free money now", "Hi, how are you?", "Win a lottery", "Meeting at 5"]
labels = [1, 0, 1, 0]  # 1 = spam, 0 = not spam

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)

joblib.dump(model, "model/spam_classifier.joblib")
joblib.dump(vectorizer, "model/vectorizer.joblib")
