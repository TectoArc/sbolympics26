'''
Portal for students' sports registration SB Olympics 2026
'''
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import threading
import time


@st.cache_resource
def create_lock():
    return threading.Lock()

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
# creds = Credentials.from_service_account_file(
#     "service.json",
#     scopes=scope)

client = gspread.authorize(creds)

worksheet= client.open("SBOLYMPICS2026").sheet1
# signup_gs = st.connection("gsheets", type='gsheets')
# st.write("connected")
# gsheet = signup_gs.open_by_key(st.secrets["connections"]["gsheets"]["spreadsheet"])
# worksheet = gsheet


def SelectSports():
    pass

def main():
    st.set_page_config(page_title="WelcomeToSBOLYMPICS2026", layout="wide")
    listed_sports = ['Sport Sword', "Trivia Night", "Treasure Hunt", "Dodgeball", "Cricket", "Darts", "Football", "Kho Kho",
                     "Ping Pong (Table Tennis)", "Basketball", "Volleyball", "Billiards (Pool)", "Backgammon", "Chess", "5k run", "100-m sprint",
                     "Relay Race", "Cake Baking", "Chill Games (Kids and Adults)", "Badminton"]
    st.multiselect(label="Which event would you like to participate in ?", options=listed_sports, 
                   placeholder="Being an audiance is not sociable ! Select at least one")


def signup_():
    st.title("Player Registration")
    with st.form("Sign Up for SBO26"):
        username = st.text_input("Name")
        Department = st.selectbox("Department", ("Swiss", "Water", "Agriculture"), index=None, placeholder=None)
        global_lock = create_lock()  # Initialize the lock in session state

        submit = st.form_submit_button("Sign up")

        if submit:
            lock_access = global_lock.acquire(timeout=0)
            if not lock_access:
                st.warning("Another participant is currently signing up. Please wait...")
                global_lock.acquire(blocking=True)
                txt = st.empty()
                for secs_rem in range(20, 0, -1):
                    txt.info(f"Please wait for {secs_rem} seconds before trying again.")
                    time.sleep(1)  # Wait for 1 second before checking again
                txt.info("🔄 You can try registering again now!")

            try:
                # LinktoGSheets(username, Department)
                st.session_state["lock_user"] = create_lock()
                st.session_state["logged in"] = True
                st.session_state["username"] = username
                st.session_state["registered_sports"] = []
                st.session_state["department"] = Department
                st.session_state["selected_sport"] = None
                st.session_state["paired_person"] = False
            finally:
                global_lock.release()
            st.switch_page("pages/SportsRegister.py")
                

def LinktoGSheets(username, Department):
    worksheet.append_row([username, Department])


if __name__ == "__main__":
    signup_()


