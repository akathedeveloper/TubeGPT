# 🎥 TubeGPT - AI Video Assistant

Transform any YouTube video into an interactive knowledge base with the power of Google Gemini AI.

<img width="2938" height="1488" alt="image" src="https://github.com/user-attachments/assets/02b8595d-74e3-46f7-8a5f-38ad1065e531" />




## ✨ Features

- 🎥 **YouTube Integration** - Load any video with captions instantly
- 🧠 **AI-Powered Q&A** - Chat with videos using Google Gemini 2.0 Flash
- ⚡ **Quick Actions** - Pre-built queries for summaries and insights
- 📊 **Smart Analytics** - Detailed video content metrics
- 🔍 **Intelligent Search** - Find relevant content through semantic search

## 🚀 Quick Start

1. **Install Dependencies**
```plaintext
pip install -r requirements.txt
```


2. **Get API Key**
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create a free Gemini API key

<img width="2928" height="1246" alt="image" src="https://github.com/user-attachments/assets/e51ead6c-ee31-4c1d-b269-c7e77f016947" />



3. **Run Application**
```plaintext
streamlit run app.py
```

4. **Start Chatting**
- Enter your API key
- Load any YouTube video
  <img width="2940" height="1658" alt="image" src="https://github.com/user-attachments/assets/cf6735c2-c062-4a21-b6a7-4f0f6f231251" />

- Ask questions about the content!
  <img width="2936" height="1052" alt="image" src="https://github.com/user-attachments/assets/0a1caa60-847d-4ace-b82f-3e63f9f51e33" />
  <img width="2940" height="1164" alt="image" src="https://github.com/user-attachments/assets/8f9f5ac8-9226-433e-ad0a-f8043ef589b0" />



## 📋 Requirements

- Python 3.8+
- Streamlit
- Google Gemini API key (free)
- Internet connection

## 🎯 How It Works

1. **Load Video** → Extracts transcript from YouTube
2. **Process Content** → Breaks transcript into smart chunks
3. **Ask Questions** → Uses AI to find relevant information
4. **Get Answers** → Receives contextual responses from video content

## 📁 Project Structure

```plaintext
tubegpt/
├── README.md
├── app.py
├── requirements.txt
├── components/
│ ├── init.py
│ ├── ui_components.py
│ ├── auth_component.py
│ ├── video_component.py
│ ├── chat_component.py
│ └── analytics_component.py
├── core/
│ ├── init.py
│ └── gemini_service.py
├── utils/
│ ├── init.py
│ └── constants.py
└── .streamlit/
└── config.toml
```


## 🔗 Links

- [**Live Demo**](https://tubegpt.streamlit.app)
- [**GitHub**](https://github.com/akathedeveloper/tubegpt)
- [**API Key**](https://makersuite.google.com/app/apikey)

## 👨‍💻 Developer

Built with ❤️ by **Adhiraj Singh**

*Powered by Google Gemini 2.0 Flash & Streamlit*

---

⭐ **Star this repo** if you find TubeGPT helpful!



