import streamlit as st
import pandas as pd
import os

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Enterprise AI Dashboard", layout="wide")

# ==============================
# HIDE DEFAULT STREAMLIT SIDEBAR MENU
# ==============================
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebarNav"] ul {display: none;}
    nav[data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebarNav"] {display: none;}
    div[data-testid="stSidebarNav"] {display: none;}
    .stSidebarNav {display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==============================
# LOAD USERS FROM EXCEL
# ==============================
@st.cache_data
def load_users():
    if not os.path.exists("users.xlsx"):
        st.error("users.xlsx not found in project folder.")
        st.stop()
    return pd.read_excel("users.xlsx")

users_df = load_users()

# ==============================
# SESSION STATE INIT
# ==============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None

# ==============================
# LOGIN FUNCTION
# ==============================
def login():
    st.title("Please Enter Username and Password")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = users_df[
            (users_df["username"] == username) &
            (users_df["password"] == password)
        ]

        if not user.empty:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# ==============================
# LOGOUT FUNCTION
# ==============================
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# ==============================
# MAIN APP
# ==============================
if not st.session_state.authenticated:
    login()
else:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")

    if st.sidebar.button("Logout"):
        logout()

    # User can select between apps after login
    app_choice = st.sidebar.radio(
        "Select Application",
        ["HR AI Platform", "AutoSphere Motors AI"]
    )

    if app_choice == "HR AI Platform":
        from pages.hr_ai import run_hr_ai
        run_hr_ai()

    elif app_choice == "AutoSphere Motors AI":
        from pages.autosphere_ai import run_autosphere
        run_autosphere()