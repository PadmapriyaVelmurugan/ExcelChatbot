import os
from flask import Flask, render_template, request, redirect
import google.generativeai as genai
import pandas as pd
import time

# Configure the API key
genai.configure(api_key="AIzaSyAuk-hoGLCDDjhW7bX8KSGQm2RxxAbFDjI")

app = Flask(__name__)

# Function to load and preview Excel data
def load_excel_data(file_path):
    # Load the Excel file into a DataFrame
    data = pd.read_excel(file_path)
    # Convert the entire DataFrame to a readable string format for the prompt
    data_context = data.to_string(index=False)
    return data_context

# Function to send a request to the model
def send_request(chat, context, question):
    try:
        # Combine context and question into a single prompt
        prompt = f"Here is the data:\n\n{context}\n\nQuestion: {question}"
        response = chat.send_message(prompt)
        return response
    except Exception as e:
        print("Error occurred:", e)
        time.sleep(5)  # Wait before retrying
        return None

# Function to start chat and ask question with the Excel data
def ask_model_with_excel(file_path, question):
    # Load Excel data and format it
    data_context = load_excel_data(file_path)

    # Start a chat with the model
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    chat = model.start_chat()

    # Send the request with the data context and question
    response = send_request(chat, data_context, question)

    if response:
        # Extract the answer from the model's response
        answer = response.candidates[0].content.parts[0].text
        return answer
    else:
        return "No response received."

# Route for the main page with form to upload file and ask question
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if file is uploaded and question is entered
        if "file" not in request.files or not request.form.get("question"):
            return redirect(request.url)

        file = request.files["file"]
        question = request.form["question"]

        if file.filename == "":
            return redirect(request.url)

        # Save the file locally in the current working directory
        file_path = os.path.join(os.getcwd(), file.filename)
        file.save(file_path)

        # Process the file and ask the question
        answer = ask_model_with_excel(file_path, question)
        return render_template("index.html", answer=answer)

    return render_template("index.html", answer=None)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=False)
