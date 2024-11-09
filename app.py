from flask import Flask, render_template, request, jsonify
import os
from Sotik import process_audio_pipeline  

app = Flask(__name__)

# Define routes for each page
@app.route('/')
def home():
    return render_template('Landing_page/LandingPage.html')

@app.route('/account')
def account_page():
    return render_template('Account_page/Acc.html')

@app.route('/avatar_creation')
def avatar_creation():
    return render_template('AvatarCreation_Pipeline/index.html')

@app.route('/chat')
def chat_page():
    return render_template('Chat/chat.html')

@app.route('/create_avatar')
def create_avatar():
    return render_template('Create_Avatar/CreateAvatar.html')

@app.route('/evaluate_pronounce', methods=['GET'])
def evaluate_pronounce():
    return render_template('Evaluate_pronounce/Evaluate_pro.html')

@app.route('/learning_journey')
def learning_journey():
    return render_template('Learing_journy/Learning_page.html')

# Route to handle feedback based on a word
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    word = data.get('word', '')
    feedback_text = pipeline(word) if word else "لم يتم إرسال كلمة."
    return jsonify({"feedback": feedback_text})

# Route to handle audio processing
@app.route('/process_audio', methods=['POST'])
def process_audio():
    audio_file = request.files['audio']
    save_path = os.path.join('User_Audios', 'uploaded_audio.wav')
    os.makedirs('User_Audios', exist_ok=True)
    audio_file.save(save_path)

    # Pass the saved audio file through the processing pipeline
    feedback = process_audio_pipeline(save_path)
    return jsonify({"feedback": feedback})

# Function to find correct pronunciation file path
def Find_Correct_path(correct_pronounce_folder, word_to_pronounce):
    correct_file = None
    try:
        for file in os.listdir(correct_pronounce_folder):
            if word_to_pronounce in file:
                correct_file = os.path.join(correct_pronounce_folder, file)
                break
        return correct_file if correct_file else "لم يتم العثور على ملف النطق للكلمة"
    except Exception as e:
        print(f"Error accessing the pronunciation folder: {e}")
        return None

# Pipeline function for word feedback simulation
def pipeline(word):
    if word:
        correct_pronounce_folder = 'C:/Users/Asus/Desktop/Allam/DownloadedVideos'
        correct_file_path = Find_Correct_path(correct_pronounce_folder, word)
        feedback = f"حاول على أن تركز على شد حرف الشين في كلمة {word}"
        return feedback
    return "الكلمة غير متوفرة."

feedback = pipeline()

if __name__ == '__main__':
    app.run(debug=True)