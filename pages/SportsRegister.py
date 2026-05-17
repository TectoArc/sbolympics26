import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(
    "service.json",
    scopes=scope)

client = gspread.authorize(creds)

worksheet= client.open("SBOLYMPICS2026").sheet1

SPORT = ["Table Tennis (Ping Pong)", "Football", "Basketball", "Volleyball", "Billiards (Pool)"]

def selectsports():
    logged_in = st.session_state["logged in"] 
    username = st.session_state["username"]
    headers = worksheet.row_values(1) # get the list of all headers - includes sports
    # check whether the user is logged in 
    if not logged_in :
        st.error("Please login first")
        st.stop()

    # Open page for registration
    st.set_page_config(page_title="WelcomeToSBOLYMPICS2026", layout="wide")
    st.title("Welcome", text_alignment='center')
    # if 'registered_sports' not in st.session_state:
    #     st.session_state['registered_sports'] = []
    with st.form("Register"):
        st.write("If you register for any events you are gay. Period !")
        
        sports = st.multiselect(label="Which event would you like to participate in ?", options=SPORT, 
                    placeholder="Being an audiance is not sociable ! Select at least one", 
                    default=st.session_state['registered_sports'])
        register = st.form_submit_button("Register")
        if register:
            records = worksheet.get_all_records()
            for idx, row in enumerate(records, start=2):
                if row["NAME"].strip().lower() == username.strip().lower():
                    for s in sports:
                        s_header_index = headers.index(s) + 1
                        if s in headers:
                            worksheet.update_cell(idx, s_header_index, 1)
                        else:
                            worksheet.update_cell(idx, s_header_index, 0)
                        st.success(f" {username} registered for {s} successfully!")
                    # sports_str = ", ".join(sports)
                    # worksheet.update_cell(idx, row[], sports_str)

    if sports not in st.session_state['registered_sports']:
        st.session_state['registered_sports'] = sports

    if register:
        st.title("Registered Sports", text_alignment='center')
        st.markdown("For notifications and updates regarding the event, join - (https://chat.whatsapp.com/IS0CcWRTOdr9u65IUsWhcE)")
    for rs in st.session_state['registered_sports']:
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.markdown(f"**{rs}**")
        with c2:
            if st.button(f"Delete", key=f"del_{rs}"):
                found = False
                records = worksheet.get_all_records()
                for idx, row in enumerate(records, start=2):
                    if row["NAME"].strip().lower() == username.strip().lower():
                        s_header_index = headers.index(rs) + 1
                        worksheet.update_cell(idx, s_header_index, "")
                        st.success(f" {username} de-registered from {rs} successfully!")
                        st.session_state["registered_sports"].remove(rs)
                        found = True
                        break

                if found:
                    st.rerun()
                else:
                    st.error("Record not found")
if __name__ == "__main__":
    selectsports()