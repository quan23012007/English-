import streamlit as st
import google.generativeai as genai
import PyPDF2
import json
import time

# --- 1. CẤU HÌNH TRANG WEB CHUẨN PRO ---
st.set_page_config(
    page_title="UEF Genius English",
    page_icon="🎓",
    layout="wide", # Giao diện tràn màn hình
    initial_sidebar_state="expanded"
)

# --- 2. CSS MAGIC (LÀM ĐẸP GIAO DIỆN) ---
st.markdown("""
<style>
    /* Font chữ Google Modern */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Style cho các nút bấm (Gradient Blue) */
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(0,0,0,0.2);
        color: #ffffff;
    }

    /* Style cho khung chứa câu hỏi (Card) */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
    }

    /* Dark mode support cho Card */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            background-color: #262730;
            border: 1px solid #3d3d3d;
        }
    }

    /* Header trang trí */
    .header-style {
        font-size: 40px;
        font-weight: 700;
        background: -webkit-linear-gradient(#eee, #333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. XỬ LÝ API KEY & SESSION ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Fallback nếu chưa cấu hình secrets (để không bị lỗi)
    if "api_key_manual" not in st.session_state:
        st.session_state.api_key_manual = ""

    # Hiện bảng nhập Key đẹp hơn
    with st.container(border=True):
        st.subheader("🔑 Authentication Required")
        api_key = st.text_input("Enter Google API Key to access Pro features:", type="password")

# Khởi tạo biến lưu điểm số (Gamification)
if 'xp_points' not in st.session_state:
    st.session_state['xp_points'] = 0
if 'level' not in st.session_state:
    st.session_state['level'] = 1

# --- 4. HÀM CORE CHỨC NĂNG ---
def get_pdf_text(uploaded_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text()
    except:
        return ""
    return text

def call_gemini(prompt):
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        with st.spinner("AI is analyzing data..."):
            response = model.generate_content(prompt)
            return json.loads(response.text)
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- 5. SIDEBAR DASHBOARD (PROFESSIONAL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("Student Portal")
    st.caption("UEF Software Engineer Future")

    st.divider()

    # Hiển thị Level & XP
    col_xp1, col_xp2 = st.columns(2)
    col_xp1.metric("Level", f"{st.session_state['level']}")
    col_xp2.metric("Total XP", f"{st.session_state['xp_points']}")

    # Thanh tiến trình giả lập
    progress = min(st.session_state['xp_points'] % 100, 100)
    st.progress(progress / 100, text=f"Next Level Progress: {progress}%")

    st.divider()

    menu = st.radio(
        "NAVIGATION",
        ["Dashboard", "📚 Reading Comprehension", "🧠 Grammar Master", "🔥 Vocabulary Blitz"],
        index=0
    )

    st.info("💡 Tip: Upload PDF để AI tạo đề sát giáo trình!")
    uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")
    pdf_context = get_pdf_text(uploaded_file) if uploaded_file else ""

# --- 6. GIAO DIỆN CHÍNH (MAIN CONTENT) ---

# === DASHBOARD (TRANG CHỦ) ===
if menu == "Dashboard":
    st.title("👋 Welcome back, Future Engineer!")
    st.markdown("### Hôm nay bạn muốn chinh phục kỹ năng nào?")

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("#### 📚 Reading")
            st.caption("Luyện đọc hiểu sâu")
            if st.button("Start Reading"): st.toast("Chuyển sang menu Reading bên trái nhé!")
    with c2:
        with st.container(border=True):
            st.markdown("#### 🧠 Grammar")
            st.caption("Nắm vững cấu trúc")
            if st.button("Start Grammar"): st.toast("Chuyển sang menu Grammar bên trái nhé!")
    with c3:
        with st.container(border=True):
            st.markdown("#### 🔥 Vocabulary")
            st.caption("Mở rộng vốn từ")
            if st.button("Start Vocab"): st.toast("Chuyển sang menu Vocab bên trái nhé!")

# === READING MODE ===
elif menu == "📚 Reading Comprehension":
    st.title("📚 Reading Comprehension")

    c1, c2 = st.columns([1, 2])
    with c1:
        topic = st.text_input("Chủ đề bài đọc:", "Technology in 2025")
        level = st.select_slider("Độ khó:", ["B1 (Dễ)", "B2 (Trung bình)", "C1 (Khó)"])
        btn_create = st.button("🚀 Generate Reading Task", use_container_width=True)

    if btn_create and api_key:
        prompt = f"""
        Tạo bài đọc hiểu tiếng Anh chủ đề '{topic}', trình độ {level}.
        Nếu có văn bản này: '{pdf_context[:1000]}', hãy dùng nó làm tư liệu.

        Output JSON: {{
            "title": "Tiêu đề bài đọc",
            "passage": "Nội dung bài đọc (khoảng 150-200 từ)",
            "quiz": [
                {{"question": "...", "options": ["A", "B", "C", "D"], "answer": "...", "explanation": "..."}}
            ]
        }}
        """
        st.session_state['reading_data'] = call_gemini(prompt)

    if 'reading_data' in st.session_state and st.session_state['reading_data']:
        data = st.session_state['reading_data']

        # Giao diện chia đôi: Bài đọc bên trái, Câu hỏi bên phải
        rc1, rc2 = st.columns([1, 1])

        with rc1:
            with st.container(border=True):
                st.subheader(data.get('title', 'Passage'))
                st.markdown(f"*{data.get('passage')}*")

        with rc2:
            st.subheader("Quiz Time")
            for i, q in enumerate(data.get('quiz', [])):
                with st.expander(f"Question {i+1}: {q['question']}", expanded=True):
                    ans = st.radio("Choose answer:", q['options'], key=f"read_{i}", label_visibility="collapsed")
                    if st.button(f"Check Answer {i+1}"):
                        if ans == q['answer']:
                            st.toast("Chính xác! +10 XP 🎉", icon="✅")
                            st.session_state['xp_points'] += 10
                            if st.session_state['xp_points'] % 100 == 0:
                                st.session_state['level'] += 1
                                st.balloons()
                        else:
                            st.toast(f"Sai rồi! Đáp án là {q['answer']}", icon="❌")
                            st.error(q['explanation'])

# === GRAMMAR MODE ===
elif menu == "🧠 Grammar Master":
    st.title("🧠 Grammar Master")

    col_input, col_act = st.columns([3, 1])
    with col_input:
        gram_topic = st.text_input("Ngữ pháp muốn ôn:", placeholder="Ví dụ: Passive Voice, Mixed Conditionals...")
    with col_act:
        st.write("") # Spacer
        st.write("")
        btn_gram = st.button("Start Quiz 🚀", use_container_width=True)

    if btn_gram and api_key:
        prompt = f"""
        Tạo 5 câu hỏi trắc nghiệm ngữ pháp KHÓ về: {gram_topic}.
        Dùng từ vựng trong file đính kèm (nếu có) để đặt câu: '{pdf_context[:500]}'
        Output JSON: list [question, options, answer, explanation]
        """
        st.session_state['gram_data'] = call_gemini(prompt)

    if 'gram_data' in st.session_state:
        for i, q in enumerate(st.session_state['gram_data']):
            with st.container(border=True):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                cols = st.columns(4)
                # Hacky way để dàn ngang options
                ans = st.radio(f"Select {i}", q['options'], key=f"gram_{i}", label_visibility="collapsed")

                if st.button(f"Submit Q{i+1}"):
                    if ans == q['answer']:
                        st.balloons()
                        st.success(f"✅ Correct! {q['explanation']}")
                        st.session_state['xp_points'] += 20 # Ngữ pháp khó nên cho nhiều điểm
                    else:
                        st.error(f"❌ Incorrect. Answer: {q['answer']}")
                        st.info(f"💡 Explanation: {q['explanation']}")

# === VOCAB MODE (Flashcard Style) ===
elif menu == "🔥 Vocabulary Blitz":
    st.title("🔥 Vocabulary Blitz")

    if st.button("🎲 Generate Random Vocab Test (From File/General)"):
        context = pdf_context if pdf_context else "General Business English"
        prompt = f"""
        Tạo 4 câu hỏi từ vựng dựa trên ngữ cảnh: {context[:2000]}.
        Tập trung vào từ đồng nghĩa/trái nghĩa.
        Output JSON: list [question, options, answer, explanation]
        """
        st.session_state['vocab_data'] = call_gemini(prompt)

    if 'vocab_data' in st.session_state:
        # Hiển thị dạng lưới 2x2
        col1, col2 = st.columns(2)
        for i, q in enumerate(st.session_state['vocab_data']):
            # Chọn cột chẵn lẻ
            with (col1 if i % 2 == 0 else col2):
                with st.container(border=True):
                    st.write(f"**#{i+1}**")
                    st.write(q['question'])
                    ans = st.selectbox("Your Answer", ["Select..."] + q['options'], key=f"vocab_{i}")

                    if ans != "Select...":
                        if ans == q['answer']:
                            st.toast("Chuẩn không cần chỉnh! +15 XP", icon="🔥")
                            st.session_state['xp_points'] += 15
                        else:
                            st.caption(f"❌ Sai. Đáp án: {q['answer']}")

if not api_key:
    st.warning("👈 Vui lòng nhập API Key ở bảng bên trái hoặc cấu hình secrets.toml")