import streamlit as st
from main import fetch_emails # Import the function from main.py
import joblib

# Load your pre-trained model and vectorizer
# Ensure these files are in a 'model' directory relative to app.py
try:
    model = joblib.load("model/spam_classifier.joblib")
    vectorizer = joblib.load("model/vectorizer.joblib")
except FileNotFoundError:
    st.error("Error: Model or vectorizer files not found. Make sure 'model/spam_classifier.joblib' and 'model/vectorizer.joblib' exist.")
    st.stop() # Stop the app if essential files are missing

st.set_page_config(page_title="Gmail Spam Scanner", page_icon="📧", layout="centered")
st.title("📧 Gmail Spam Scanner")
st.markdown("Enter your Gmail credentials to scan your inbox for spam.")

# Get email and password from user input in the Streamlit app
# These values will be passed to fetch_emails
user_email = st.text_input("Enter your Gmail address", help="This should be the email address you want to scan.")
user_password = st.text_input("Enter your Gmail App Password", type="password", help="**Important:** Use an App Password, not your regular Gmail password. See Google's documentation for how to generate one.")

# Check if both fields are filled before enabling the button
if user_email and user_password:
    if st.button("Scan My Gmail Inbox"):
        with st.spinner("Fetching and scanning emails... This may take a moment."):
            try:
                # Pass the user-provided email and password to the fetch_emails function
                emails = fetch_emails(user_email, user_password)

                if emails:
                    st.success(f"Scanned {len(emails)} emails. Here are the results:")
                    for idx, (subject, content) in enumerate(emails, 1):
                        # Combine subject and content for classification
                        text_to_classify = subject + " " + content

                        # Transform the text using the loaded vectorizer
                        X = vectorizer.transform([text_to_classify])

                        # Make a prediction
                        prediction = model.predict(X)[0] # model.predict returns an array

                        # Determine the result string
                        result_emoji = "🚫" if prediction == 1 else "✅"
                        result_text = "Spam" if prediction == 1 else "Not Spam"

                        # Display the results in an expander
                        with st.expander(f"{idx}. {subject} - {result_emoji} {result_text}"):
                            st.write("📨 Full Email Body:")
                            # Use st.code or st.text for preformatted text like email bodies
                            st.text(content.strip())
                else:
                    st.info("No emails were fetched or processed. Please check your credentials and try again, or you might not have recent emails in your inbox/spam.")
            except Exception as e:
                st.error(f"An error occurred during email fetching or scanning: {e}")
                st.warning("Please ensure your Gmail address and App Password are correct, and that IMAP is enabled for your Gmail account.")
else:
    st.warning("Please enter your Gmail address and App Password to enable the 'Scan My Gmail Inbox' button.")

st.markdown("---")
st.markdown("""
**How to get a Gmail App Password:**
1. Go to your Google Account settings.
2. Navigate to 'Security'.
3. Under 'How you sign in to Google', select 'App passwords'. (You might need to sign in).
4. Follow the instructions to generate a new app password. Select 'Mail' for the app and 'Other' for the device.
5. Copy the 16-character password it generates (without spaces) and paste it into the 'Gmail App Password' field above.
""")
