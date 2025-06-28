import streamlit as st
from main import fetch_emails
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
# Load model
model = joblib.load("model/spam_classifier.joblib")
vectorizer = joblib.load("model/vectorizer.joblib")

st.title("📧 Gmail Spam Scanner")
EMAIL = st.text_input("Enter your Gmail address")
PASSWORD = st.text_input("Enter your Gmail App Password", type="password")
if st.button("Scan My Gmail Inbox"):
    with st.spinner("Fetching and scanning emails..."):
        emails = fetch_emails()
        for idx, (subject, content) in enumerate(emails, 1):
            text = subject + " " + content
            X = vectorizer.transform([text])
            prediction = model.predict(X)[0]
            result = "\n🚫 Spam" if prediction == 1 else "\n✅ Not Spam"
            with st.expander(f"{idx}. {subject} - {result}"):
               st.write("📨 Full Email Body:")
               st.text(content.strip())

