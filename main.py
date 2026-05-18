'''
Portal for students' sports registration SB Olympics 2026
'''
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

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
    st.write("If you register for any events you are gay. Period !")
    
    st.multiselect(label="Which event would you like to participate in ?", options=["Billiards (Pool)", "Basketball", "Football", "Volleyball", "Table Tennis (Ping Pong)"], 
                   placeholder="Being an audiance is not sociable ! Select at least one")


def signup_():
    st.title("User Registration")
    # choice = st.radio("Are you already registerd ?", ["Sign up", "Login"])
    # if choice == 'Login':
    #     login_page()
    # else:
    #     signup_page()

    with st.form("Sign Up for SBO26"):
        username = st.text_input("Name")
        password = st.text_input("BGU ID", type="password")
        Department = st.text_input("Department")
        submit = st.form_submit_button("Sign up")

        if submit:
            LinktoGSheets(username, Department)
            st.session_state["logged in"] = True
            st.session_state["username"] = username
            st.session_state["registered_sports"] = []
            st.session_state["department"] = Department
            st.session_state["selected_sport"] = None
            st.session_state["paired_person"] = False
            st.switch_page("pages/SportsRegister.py")

def LinktoGSheets(username, Department):
    data = worksheet.get_all_records()
    # for row in data:
    #     if row[0].strip().lower() == username.strip().lower():
    #         print("Participant already registered. PLease login using BGU ID")
    #         return 
    #     else:
            # st.success("You are registered !")

    worksheet.append_row([username, Department])
    # new_participant = pd.DataFrame([{"Name": username, 
    #                           "Department":Department}])
    # update = pd.concat([data, new_participant], ignore_index=True)
    # worksheet.update(worksheet="Registered Participants", data=update)


if __name__ == "__main__":
    signup_()


