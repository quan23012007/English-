import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import pypdf
from PIL import Image

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="App Tiếng Anh Đa Năng", page_icon="🔥")

# --- CẤU HÌNH API ---
# 👇 DÁN API KEY CỦA BẠN VÀO ĐÂY
api_key = "AIzaSyAb5iLa6GXW3jAYMlZcnsWIG29k2ixnAAc"

if api_key == "AIzaSy_Dán_Mã_Của_Bạn_Vào_Đây_Nhé_xxxxx":
    api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ Chưa có API Key! Vui lòng dán mã vào code.")
    st.stop()

genai.configure(api_key=api_key)

# 👉 SỬA LỖI: Chuyển về model 'gemini-pro' (Ổn định hơn)
model = genai.GenerativeModel('gemini-pro')

# --- HÀM HỖ TRỢ ---
def get_gemini_response(prompt, image=None):
    try:
        if image:
            # Gemini Pro không xem được ảnh, nên ta thông báo khéo cho người dùng
            return "⚠️ Xin lỗi, phiên bản AI này chỉ hỗ trợ đọc File PDF (văn bản), chưa hỗ trợ xem Hình ảnh. Bạn hãy thử upload file PDF nhé!"
        else:
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        return f"Lỗi AI: {e}"

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = "audio_temp.mp3"
        tts.save(filename)
        return filename
    except:
        return None

def read_pdf(file):
    pdf_reader = pypdf.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# --- GIAO DIỆN CHÍNH ---
st.title("🔥 English Master AI")

with st.sidebar:
    st.header("🎛️ Menu")
    skill = st.radio("Chọn kỹ năng:",
        ["📖 Reading", "🎧 Listening", "📝 Vocabulary (Từ vựng)", "✍️ Grammar"])

    st.divider()

    if skill != "📝 Vocabulary (Từ vựng)":
        level = st.select_slider("Trình độ:", options=["A1", "A2", "B1", "B2", "C1", "C2"])
        topic = st.text_input("Chủ đề:", value="Daily Life")
        btn_start = st.button("🚀 Bắt đầu học")
    else:
        st.info("👈 Phần Từ vựng có chế độ tải file PDF!")

# --- XỬ LÝ NỘI DUNG ---
if skill == "📝 Vocabulary (Từ vựng)":
    st.header("📝 Học từ vựng thông minh")

    tab1, tab2 = st.tabs(["🔤 Theo Chủ đề", "📂 Tải File PDF"])

    with tab1:
        vocab_topic = st.text_input("Nhập chủ đề muốn học:", value="Travel")
        vocab_level = st.select_slider("Chọn trình độ:", ["A1", "A2", "B1", "B2", "C1", "C2"], key="v_lvl")
        if st.button("Tạo danh sách từ"):
            prompt = f"Liệt kê 10 từ vựng tiếng Anh hay nhất về chủ đề '{vocab_topic}' trình độ {vocab_level}. Trình bày dạng bảng."
            st.markdown(get_gemini_response(prompt))

    with tab2:
        st.write("Tải lên tài liệu PDF (Sách, Bài tập...) để AI rút từ vựng.")
        # Chỉ cho phép file pdf
        uploaded_file = st.file_uploader("Chọn file PDF:", type=['pdf'])

        if uploaded_file and st.button("🔍 Rút từ vựng từ file này"):
            with st.spinner("Đang đọc tài liệu..."):
                if uploaded_file.name.endswith('.pdf'):
                    content = read_pdf(uploaded_file)
                    prompt = f"""
                    Dựa vào nội dung tài liệu này: {content[:3000]}...
                    Hãy tìm ra 10 từ vựng quan trọng nhất cần học.
                    Giải thích nghĩa và trình bày dạng bảng.
                    """
                    result = get_gemini_response(prompt)
                    st.markdown("### 📑 Kết quả phân tích:")
                    st.markdown(result)
                else:
                    st.error("Vui lòng chọn file PDF.")

# CÁC KỸ NĂNG KHÁC (GIỮ NGUYÊN)
elif 'btn_start' in locals() and btn_start:
    with st.spinner("AI đang làm việc..."):
        if skill == "📖 Reading":
            prompt = f"Viết bài đọc chủ đề '{topic}' trình độ {level}. Kèm 3 câu hỏi trắc nghiệm."
            st.markdown(get_gemini_response(prompt))

        elif skill == "🎧 Listening":
            script = get_gemini_response(f"Viết đoạn hội thoại tiếng Anh về '{topic}' trình độ {level}. Chỉ viết tiếng Anh.")
            st.subheader("🎧 Bài nghe")
            audio = text_to_speech(script)
            if audio: st.audio(audio)
            with st.expander("Xem lời thoại"): st.write(script)

        elif skill == "✍️ Grammar":
            prompt = f"Giải thích 1 điểm ngữ pháp về '{topic}' trình độ {level}. Cho ví dụ và bài tập."
            st.markdown(get_gemini_response(prompt))
