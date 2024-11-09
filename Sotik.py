import sounddevice as sd
from scipy.io.wavfile import write
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, AutoProcessor, AutoModelForCTC
import torch
import json, requests
import torchaudio
from pydub import AudioSegment
import os

def record_audio():
    duration = 5  # seconds
    sample_rate = 44100  # 44.1 kHz
    directory = "User_Audios"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, "output.wav")
    print("Recording...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
    sd.wait()
    print("Recording finished.")
    write(file_path, sample_rate, audio_data)
    print(f"Audio saved as {file_path}")
    return file_path

def preprocess_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export("processed.ogg", format="ogg")
    waveform, sample_rate = torchaudio.load("processed.ogg")
    return waveform

def Speech_To_Text(waveform):
    processor = AutoProcessor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-arabic")
    model = AutoModelForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-arabic")
    input_values = processor(waveform.squeeze(), sampling_rate=16000, return_tensors="pt").input_values
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.decode(predicted_ids[0])
    return transcription

def tashkeel(transcription):
    url = 'https://farasa.qcri.org/webapi/diacritize/'
    api_key = "CteGLOJgRebKsiUwOi"
    payload = {'text': transcription, 'api_key': api_key}
    data = requests.post(url, data=payload)
    result = json.loads(data.text)
    return result['text']

def Generate_Access_Token():
    url = 'https://iam.cloud.ibm.com/identity/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey': 'mc37vqh646rMQwZblc3tFb1Xw65Qf6G-5w9pDgbULszt'
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

    res_format = response.json()
    YOUR_ACCESS_TOKEN = res_format['access_token']
    return res_format['access_token']


def compare_pronunciation(user_word, correct_word, your_access_token):
    url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    
    # Prepare the body with formatted user_word and correct_word in the input
    body = {
        "input": f"""<s> [INST]<<SYS>>
        تلقى النموذج كلمتين: الكلمة الأصلية التي كان من المفترض أن ينطقها المستخدم {correct_word}، والكلمة التي نطقها المستخدم فعلياً {user_word}.
        
        قارن بين النطقين من خلال تحليل الفروقات بين الكلمتين من حيث الحروف والحركات (مثل الضمة، الفتحة، الكسرة، والسكون).
        
        إذا كان النطق غير مطابق، قدم تغذية راجعة واضحة وسهلة الفهم توضح للمستخدم الحروف أو الحركات التي تم نطقها بشكل غير صحيح، مع توجيهات لتحسين نطقه.
        
        استخدم لغة بسيطة وتجنب المصطلحات التقنية لسهولة الفهم.
        
        توضيحات إضافية للتغذية الراجعة:
        
        إذا كان النطق مطابقاً تماماً، أخبر المستخدم أن نطقه صحيح.
        إذا وُجدت اختلافات، وضح للمستخدم الحروف أو الحركات التي نطقها بشكل غير دقيق.
        قدم نصائح مفيدة لتحسين النطق، مثل كيفية نطق حرف معين أو ضبط حركة معينة بشكل أدق.
        <</SYS>>""",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "repetition_penalty": 1
        },
        "model_id": "sdaia/allam-1-13b-instruct",
        "project_id": "75af9c92-9a13-4cfe-ac8a-cb4ee623c49a"
    }

    # Set headers with Authorization
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {your_access_token}"
    }

    # Send the POST request
    response = requests.post(url, headers=headers, json=body)

    # Check for non-200 response
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    # Parse the JSON response
    data = response.json()
    return data

def chat_bot(your_access_token):
    url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

    body = {
    "input": """<s> [INST]<<SYS>>

    أنت نموذج لغة متخصص في تقديم إجابات دقيقة وموثوقة حول اللغة العربية. يمكنك الإجابة عن أسئلة تتعلق بالنحو والصرف والمعاني والمفردات والأدب والشعر والثقافة العربية بشكل عام. يجب أن تكون الإجابات مبنية على قواعد اللغة العربية والتراث اللغوي مع توضيح المفاهيم اللغوية بشكل يسهل فهمه للمستخدمين من مختلف المستويات.

    يجب عليك تقديم الأمثلة والتفسيرات عند الحاجة وتوضيح التفاصيل اللغوية دون تعقيد. كن دقيقًا ومباشرًا في الإجابات، مع مراعاة الأمانة العلمية وتجنب الاجتهادات الشخصية.
    <</SYS>>

    اهلا [/INST]  أهلاً وسهلاً بك! كيف يمكنني مساعدتك اليوم في مجال اللغة العربية؟ إذا كان لديك سؤال حول النحو، الصرف، المعاني، المفردات، الأدب، الشعر، أو الثقافة العربية، فلا تتردد في طرحه وسأكون سعيداً للإجابة عنه.  </s><s> [INST] اشرح لي قواعد التنوين [/INST]  التنوين هو علامة تشكيل توضع على آخر الأسماء المعربة للدلالة على حالة معينة. قواعد التنوين في اللغة العربية هي كالتالي:

    1. التنوين بالفتح: يُضاف التنوين بالفتح إلى آخر الاسم للدلالة على حالة النصب. مثال: قرأتُ كتابًا مفيدًا. في هذا المثال، \"كتابًا\" هو اسم منصوب بسبب التنوين بالفتح.

    2. التنوين بالضم: يُضاف التنوين بالضم إلى آخر الاسم للدلالة على حالة الرفع. مثال: هذا طالبٌ مجتهدٌ. في هذا المثال، \"طالبٌ\" هو اسم مرفوع بسبب التنوين بالضم.

    3. التنوين بالكسر: يُضاف التنوين بالكسر إلى آخر الاسم للدلالة على حالة الجر. مثال: زرتُ صديقًا قديمًا. في هذا المثال، \"صديقًا\" هو اسم مجرور بسبب التنوين بالكسر.

    يجب ملاحظة أن الأسماء الممنوعة من الصرف لا تقبل التنوين. أيضاً، الأسماء المعرفة بـ \"ال\" لا تقبل التنوين.

    للتنوين ثلاثة أشكال: تنوين الفتح (ً)، تنوين الضم (ٌ)، وتنوين الكسر (ٍ). تُضاف هذه الأشكال إلى آخر الأسماء المعربة للدلالة على حالات الإعراب المختلفة.  </s><s> [INST] ماهو حكم الصوم  [/INST]  الصوم في الإسلام هو أحد الأركان الخمسة الأساسية ويعتبر عبادة مهمة جداً. حكم الصوم هو واجب على كل مسلم بالغ وعاقل وقادر على تحمله. يُفرض الصوم خلال شهر رمضان المبارك، حيث يمتنع المسلمون عن الطعام والشراب والجماع من الفجر حتى المغرب.

    الصوم له فوائد روحية وجسدية واجتماعية. يعتبر فرصة للمسلمين لتقوية إيمانهم وزيادة التقوى والصبر. كما يساعد الصوم على تعزيز التكافل الاجتماعي بين المسلمين من خلال تقديم الزكاة والصدقات للمحتاجين.

    إذا كنت تبحث عن مزيد من المعلومات حول الصوم وأحكامه وفوائده، يمكنك الرجوع إلى المصادر الدينية والكتب الإسلامية الموثوقة.  </s><s> [INST]""",
    "parameters": {
        "decoding_method": "greedy",
        "max_new_tokens": 900,
        "repetition_penalty": 1
    },
    "model_id": "sdaia/allam-1-13b-instruct",
    "project_id": "75af9c92-9a13-4cfe-ac8a-cb4ee623c49a"
    }

    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " +your_access_token
    }

    response = requests.post(
    url,
    headers=headers,
    json=body
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

def process_audio_pipeline(file_path):
    waveform = preprocess_audio(file_path)
    transcription = Speech_To_Text(waveform)
    user_word = tashkeel(transcription)
    correct_word = "الشمس"  # Replace with the correct word for comparison
    your_access_token = Generate_Access_Token()
    feedback = compare_pronunciation(user_word, correct_word, your_access_token)
    chat_bot_response = chat_bot(your_access_token)
    return feedback