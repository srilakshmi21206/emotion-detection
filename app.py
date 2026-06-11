import streamlit as st
import numpy as np
from deepface import DeepFace
from PIL import Image

# Page config
st.set_page_config(page_title="Emotion Detection", page_icon="🎭", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460); }
    .title { text-align: center; font-size: 2.8em; font-weight: bold;
             background: linear-gradient(90deg, #f093fb, #f5576c, #4facfe);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #aaa; font-size: 1.1em; margin-bottom: 20px; }
    .emotion-card { padding: 20px; border-radius: 20px; text-align: center;
                    margin: 10px 0; backdrop-filter: blur(10px); }
    .fact-card { padding: 15px; border-radius: 15px; margin: 10px 0;
                 background: linear-gradient(135deg, #667eea22, #764ba222); }
    .music-card { padding: 15px; border-radius: 15px; margin: 5px 0;
                  background: linear-gradient(135deg, #f093fb22, #f5576c22); }
    .history-card { padding: 10px; border-radius: 10px; margin: 5px 0;
                    background: rgba(255,255,255,0.05); }
    .footer { text-align: center; color: #666; font-size: 0.8em; margin-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# Data
emotion_emoji = {
    'happy': '😊', 'sad': '😢', 'angry': '😠',
    'surprise': '😲', 'fear': '😨', 'disgust': '🤢', 'neutral': '😐'
}

emotion_gradient = {
    'happy': 'linear-gradient(135deg, #f6d365, #fda085)',
    'sad': 'linear-gradient(135deg, #a1c4fd, #c2e9fb)',
    'angry': 'linear-gradient(135deg, #ff416c, #ff4b2b)',
    'surprise': 'linear-gradient(135deg, #f093fb, #f5576c)',
    'fear': 'linear-gradient(135deg, #4776e6, #8e54e9)',
    'disgust': 'linear-gradient(135deg, #56ab2f, #a8e063)',
    'neutral': 'linear-gradient(135deg, #bdc3c7, #2c3e50)'
}

emotion_facts = {
    'happy': [
        "😊 Smiling releases endorphins, dopamine, and serotonin!",
        "🧠 Happiness can be contagious — seeing someone smile activates mirror neurons!",
        "💪 Happy people live 7-10 years longer on average!",
        "🌟 Laughter boosts your immune system by 40%!"
    ],
    'sad': [
        "😢 Crying releases stress hormones and actually makes you feel better!",
        "🧠 Sadness helps you pay more attention to details!",
        "🎨 Many great artworks were created during sad moments!",
        "💙 Sadness makes you more empathetic towards others!"
    ],
    'angry': [
        "😠 Anger increases testosterone and decreases cortisol!",
        "⚡ Anger can boost creativity and problem-solving!",
        "🧠 Controlled anger can be a powerful motivator!",
        "💪 Anger helped our ancestors survive dangerous situations!"
    ],
    'surprise': [
        "😲 Surprise lasts only 1/25th of a second — the shortest emotion!",
        "🧠 Surprise activates the same brain regions as curiosity!",
        "👀 Your eyes widen during surprise to take in more visual information!",
        "⚡ Surprise boosts memory — surprised moments are remembered longer!"
    ],
    'fear': [
        "😨 Fear increases your strength and speed temporarily!",
        "🧠 Fear and excitement trigger the same brain chemicals!",
        "👁️ Pupils dilate during fear to improve night vision!",
        "💓 Fear makes your heart beat faster to pump blood to muscles!"
    ],
    'disgust': [
        "🤢 Disgust evolved to protect us from poisonous foods!",
        "🧠 Disgust and moral judgment share the same brain region!",
        "👃 The nose wrinkles during disgust to reduce smell intake!",
        "🛡️ Disgust is one of the 6 universal emotions across all cultures!"
    ],
    'neutral': [
        "😐 Neutral expressions are great for poker players!",
        "🧠 A neutral face is often perceived as trustworthy!",
        "🎭 Actors train for years to master the neutral expression!",
        "💆 Neutral expression is linked to mindfulness and calm!"
    ]
}

emotion_music = {
    'happy': [
        "🎵 Happy — Pharrell Williams",
        "🎵 Can't Stop the Feeling — Justin Timberlake",
        "🎵 Uptown Funk — Bruno Mars",
        "🎵 Good as Hell — Lizzo"
    ],
    'sad': [
        "🎵 Someone Like You — Adele",
        "🎵 The Night We Met — Lord Huron",
        "🎵 Fix You — Coldplay",
        "🎵 Let Her Go — Passenger"
    ],
    'angry': [
        "🎵 Break Stuff — Limp Bizkit",
        "🎵 Killing in the Name — Rage Against the Machine",
        "🎵 Given Up — Linkin Park",
        "🎵 Bodies — Drowning Pool"
    ],
    'surprise': [
        "🎵 What?! — Various Artists",
        "🎵 Surprise Symphony — Haydn",
        "🎵 Wow — Post Malone",
        "🎵 OMG — Usher"
    ],
    'fear': [
        "🎵 Thriller — Michael Jackson",
        "🎵 Enter Sandman — Metallica",
        "🎵 Disturbia — Rihanna",
        "🎵 Monster — Imagine Dragons"
    ],
    'disgust': [
        "🎵 Yuck — Various Artists",
        "🎵 Bad Guy — Billie Eilish",
        "🎵 Creep — Radiohead",
        "🎵 Toxic — Britney Spears"
    ],
    'neutral': [
        "🎵 Clair de Lune — Debussy",
        "🎵 Weightless — Marconi Union",
        "🎵 Experience — Ludovico Einaudi",
        "🎵 Comptine d'un autre été — Yann Tiersen"
    ]
}

# Initialize history
if 'history' not in st.session_state:
    st.session_state.history = []

def analyze_emotion(image_array):
    try:
        result = DeepFace.analyze(image_array, actions=['emotion'], enforce_detection=False)
        if isinstance(result, list):
            result = result[0]
        emotion = result['dominant_emotion']
        scores = result['emotion']
        return emotion, scores
    except Exception as e:
        return None, None

def show_results(emotion, scores):
    emoji = emotion_emoji.get(emotion, '😐')
    gradient = emotion_gradient.get(emotion, 'linear-gradient(135deg, #bdc3c7, #2c3e50)')
    confidence = scores[emotion]

    # Add to history
    st.session_state.history.append(f"{emoji} {emotion.capitalize()} ({confidence:.1f}%)")

    # Emotion card
    st.markdown(f"""
        <div class="emotion-card" style="background: {gradient};">
            <h1 style="font-size: 4em; margin:0;">{emoji}</h1>
            <h2 style="color: white; margin:5px 0;">{emotion.upper()}</h2>
            <h3 style="color: white; margin:0;">Confidence: {confidence:.1f}%</h3>
        </div>
    """, unsafe_allow_html=True)

    # Scores
    st.subheader("📊 All Emotion Scores")
    col1, col2 = st.columns(2)
    emotions_sorted = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for i, (emo, score) in enumerate(emotions_sorted):
        em = emotion_emoji.get(emo, '😐')
        with col1 if i % 2 == 0 else col2:
            st.write(f"{em} **{emo.capitalize()}** — {score:.1f}%")
            st.progress(int(score))

    # Fun fact
    import random
    st.divider()
    st.subheader("🧠 Fun Fact About This Emotion")
    facts = emotion_facts.get(emotion, [])
    if facts:
        fact = random.choice(facts)
        st.markdown(f"""
            <div class="fact-card">
                <p style="color: #e0e0e0; font-size: 1.1em; margin:0;">{fact}</p>
            </div>
        """, unsafe_allow_html=True)

    # Music
    st.divider()
    st.subheader("🎵 Music For Your Mood")
    songs = emotion_music.get(emotion, [])
    for song in songs:
        st.markdown(f"""
            <div class="music-card">
                <p style="color: #f0e0ff; margin:0;">{song}</p>
            </div>
        """, unsafe_allow_html=True)

# Header
st.markdown('<div class="title">🎭 Emotion Detection System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered facial emotion recognition with music & fun facts!</div>', unsafe_allow_html=True)
st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["📸 Photo Upload", "📷 Webcam", "📝 History"])

# Tab 1
with tab1:
    uploaded_file = st.file_uploader("Upload a face image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Uploaded Image", use_column_width=True)
        with st.spinner("🔍 Reading your emotion..."):
            emotion, scores = analyze_emotion(img_array)
        if emotion:
            show_results(emotion, scores)
        else:
            st.error("❌ No face detected! Please upload a clear face image.")

# Tab 2
with tab2:
    img_file = st.camera_input("📷 Take a photo!")
    if img_file is not None:
        image = Image.open(img_file)
        img_array = np.array(image)
        with st.spinner("🔍 Reading your emotion..."):
            emotion, scores = analyze_emotion(img_array)
        if emotion:
            show_results(emotion, scores)
        else:
            st.error("❌ No face detected! Try again with better lighting.")

# Tab 3 - History
with tab3:
    st.subheader("📝 Emotion History")
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            st.markdown(f"""
                <div class="history-card">
                    <p style="color: #e0e0e0; margin:0;">#{len(st.session_state.history)-i}. {entry}</p>
                </div>
            """, unsafe_allow_html=True)
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No emotions detected yet! Upload a photo or use webcam.")

st.divider()
st.markdown('<div class="footer">Built with DeepFace & Streamlit | Emotion Detection System</div>', unsafe_allow_html=True)