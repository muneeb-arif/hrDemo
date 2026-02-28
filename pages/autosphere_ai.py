import streamlit as st
import os
import pandas as pd
import random
from datetime import datetime
import json
import ast

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from utils.openai_client import get_openai_client

def run_autosphere():

    client = get_openai_client()
    
    # Add custom styling for AutoSphere page
    st.markdown("""
    <style>
        .autosphere-header {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        .user-message {
            background: #e3f2fd;
            margin-left: 20%;
        }
        .bot-message {
            background: #f5f5f5;
            margin-right: 20%;
        }
        .stChatInput {
            border-radius: 10px;
        }
        .stForm {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }
        .stTextInput > div > div > input:focus {
            border-color: #f5576c;
            box-shadow: 0 0 0 3px rgba(245,87,108,0.1);
        }
        .stSelectbox > div > div {
            border-radius: 10px;
        }
        .stButton > button {
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="autosphere-header">
        <h1 style='margin: 0; color: white;'>🚗 AutoSphere Motors AI Assistant</h1>
        <p style='margin: 0.5rem 0 0 0; color: rgba(255,255,255,0.9);'>
            Your Intelligent Automotive Assistant • Book Services • Get Answers
        </p>
    </div>
    """, unsafe_allow_html=True)

    LLM_MODEL = "gpt-4o"
    EMBED_MODEL = "text-embedding-3-large"
    BOOKINGS_FILE = "bookings.xlsx"

    # =====================================================
    # LOAD VECTOR STORE
    # =====================================================
    @st.cache_resource
    def load_vectorstore():
        embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
        if not os.path.exists("vectorstore"):
            loader = Docx2txtLoader("autosphere_policy.docx")
            documents = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
            docs = splitter.split_documents(documents)
            vectorstore = FAISS.from_documents(docs, embeddings)
            vectorstore.save_local("vectorstore")
        else:
            vectorstore = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
        return vectorstore

    vectorstore = load_vectorstore()

    # =====================================================
    # HELPER FUNCTIONS
    # =====================================================
    def generate_booking_id():
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = random.randint(1000, 9999)
        return f"AS-{date_part}-{random_part}"

    def save_to_excel(data_dict):
        """Save booking to a single unified bookings.xlsx file"""
        df = pd.DataFrame([data_dict])
        if os.path.exists(BOOKINGS_FILE):
            existing_df = pd.read_excel(BOOKINGS_FILE)
            updated_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            updated_df = df
        updated_df.to_excel(BOOKINGS_FILE, index=False)

    def classify_intent(user_message):
        prompt = f"""
        Classify user intent:
        - service_booking
        - test_drive_booking
        - general_question

        Message: {user_message}
        Return only intent in lowercase.
        """
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()

    def extract_booking_details(user_text):
        prompt = f"""
        Extract only the booking details from the text and return as JSON with double quotes.
        Do not add extra text.

        Fields required:
        - Name
        - Phone
        - Vehicle Model
        - Preferred Date (YYYY-MM-DD)

        Text:
        {user_text}
        """
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        text = response.choices[0].message.content.strip()

        # Try JSON parsing
        try:
            data = json.loads(text)
            if all(k in data for k in ["Name", "Phone", "Vehicle Model", "Preferred Date"]):
                return data
        except:
            try:
                data = ast.literal_eval(text)
                if isinstance(data, dict) and all(k in data for k in ["Name", "Phone", "Vehicle Model", "Preferred Date"]):
                    return data
            except:
                pass

        # Fallback: line-by-line parsing
        data = {}
        lines = user_text.splitlines()
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().lower()
                val = val.strip()
                if key in ["name", "phone", "vehicle model", "preferred date"]:
                    data[key.title()] = val
        if len(data) == 4:
            return data
        return None

    # =====================================================
    # CREATE TABS
    # =====================================================
    tab1, tab2, tab3 = st.tabs(["💬 AI Assistant", "📝 Book a Service / Test Drive", "🔎 Search Booking"])

    # =====================================================
    # TAB 1 — AI Assistant + Chat Booking
    # =====================================================
    with tab1:
        if "auto_chat_history" not in st.session_state:
            st.session_state.auto_chat_history = []
        if "booking_flow" not in st.session_state:
            st.session_state.booking_flow = None

        user_input = st.chat_input("Ask anything about AutoSphere...")

        if user_input:
            st.session_state.auto_chat_history.append(("User", user_input))

            # Booking flow
            if st.session_state.booking_flow:
                extracted_data = extract_booking_details(user_input)
                if extracted_data:
                    booking_type = st.session_state.booking_flow
                    extracted_data["Booking Type"] = "Service" if booking_type=="service_booking" else "Test Drive"
                    extracted_data["DateTime"] = datetime.now()
                    extracted_data["Booking ID"] = generate_booking_id()
                    save_to_excel(extracted_data)
                    confirm_msg = f"✅ {extracted_data['Booking Type']} Booking Confirmed!\nBooking ID: {extracted_data['Booking ID']}"
                    st.session_state.auto_chat_history.append(("Bot", confirm_msg))
                    st.session_state.booking_flow = None
                else:
                    st.session_state.auto_chat_history.append(
                        ("Bot", "⚠️ Could not extract details. Please provide in format:\nName, Phone, Vehicle Model, Preferred Date (YYYY-MM-DD)")
                    )
            else:
                intent = classify_intent(user_input)
                if intent in ["service_booking", "test_drive_booking"]:
                    st.session_state.booking_flow = intent
                    st.session_state.auto_chat_history.append(
                        ("Bot", f"Sure! Let's book your {'Service' if intent=='service_booking' else 'Test Drive'}.\nPlease provide Name, Phone, Vehicle Model, Preferred Date (YYYY-MM-DD) in one message.")
                    )
                else:
                    docs = vectorstore.similarity_search(user_input, k=3)
                    context = "\n".join([doc.page_content for doc in docs])
                    response = client.chat.completions.create(
                        model=LLM_MODEL,
                        messages=[
                            {"role": "system", "content": "You are AutoSphere AI."},
                            {"role": "user", "content": context + "\nUser: " + user_input}
                        ],
                        temperature=0.2
                    )
                    st.session_state.auto_chat_history.append(("Bot", response.choices[0].message.content))

        # Display chat
        for role, message in st.session_state.auto_chat_history:
            if role == "User":
                st.chat_message("user").write(message)
            else:
                st.chat_message("assistant").write(message)

    # =====================================================
    # TAB 2 — Manual Booking Form
    # =====================================================
    with tab2:
        st.subheader("📝 Book a Service / Test Drive (Manual Form)")
        with st.form(key="booking_form"):
            booking_type = st.selectbox("Booking Type", ["Service", "Test Drive"])
            name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            vehicle_model = st.text_input("Vehicle Model")
            preferred_date = st.date_input("Preferred Date")
            submit_btn = st.form_submit_button("Submit Booking")

        if submit_btn:
            if not all([name, phone, vehicle_model]):
                st.warning("⚠️ Please fill all fields before submitting.")
            else:
                booking_data = {
                    "Booking Type": booking_type,
                    "Name": name,
                    "Phone": phone,
                    "Vehicle Model": vehicle_model,
                    "Preferred Date": preferred_date.strftime("%Y-%m-%d"),
                    "DateTime": datetime.now(),
                    "Booking ID": generate_booking_id()
                }
                save_to_excel(booking_data)
                st.success(f"✅ {booking_type} Booking Confirmed! Your Booking ID: {booking_data['Booking ID']}")

    # =====================================================
    # TAB 3 — Search Booking
    # =====================================================
    with tab3:
        st.subheader("🔎 Search Booking")
        search_id = st.text_input("Booking ID", key="search_id")
        search_phone = st.text_input("Phone Number", key="search_phone")
        search_type = st.selectbox("Booking Type (optional)", ["", "Service", "Test Drive"], key="search_type")

        if st.button("Search", key="search_button"):
            results = []
            if os.path.exists(BOOKINGS_FILE):
                df = pd.read_excel(BOOKINGS_FILE)
                df.columns = df.columns.str.strip().str.lower()
                result = df.copy()

                if search_id:
                    result = result[result["booking id"] == search_id]
                if search_phone:
                    result = result[result["phone"] == search_phone]
                if search_type:
                    result = result[result["booking type"].str.lower() == search_type.lower()]
                if not result.empty:
                    results.append(result)

            if results:
                final_df = pd.concat(results, ignore_index=True)
                st.success("Booking Found!")
                st.dataframe(final_df)
            else:
                st.error("No booking found.")