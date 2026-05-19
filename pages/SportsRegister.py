import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from main import create_lock


global_lock = create_lock()  # Initialize the lock in session state
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope)

client = gspread.authorize(creds)

worksheet= client.open("SBOLYMPICS2026").sheet1

SPORT = ["Table Tennis (Ping Pong)", "Football", "Basketball", "Volleyball", "Billiards (Pool)"]

def selectsports():
    logged_in = st.session_state["logged in"] 
    username = st.session_state["username"]
    department = st.session_state["department"]
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
        st.markdown(
        """
        <style>
        .stMultiSelect div[role="listbox"] {
            max-height: 100px; /* Adjust this height as needed */
            overflow-y: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
        )
        sports = st.multiselect(label="Which event would you like to participate in ?", options=SPORT, 
                    placeholder="Being an audiance is not sociable ! Select at least one", 
                    default=st.session_state['registered_sports'])
        register = st.form_submit_button("Register")
        if register:
            lock_access = global_lock.acquire(timeout=0)
            if not lock_access:
                st.warning("Other players are also registering. Please wait while we process your registration...")
                global_lock.acquire(blocking=True)

            try:
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
            finally:
                global_lock.release()
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
    _TeamUP(worksheet, client.open("SBOLYMPICS2026"), username, department)
    return 

def _TeamUP(sheet, sheet2, username, department):
    paired_sheet = sheet2.worksheet("Paired_Sports")
    sports_to_pair = ["Billiards (Pool)", "Table Tennis (Ping Pong)"]
    records = sheet.get_all_records()
    all_sports = list(records[0].keys())
    st.title("Pairing")
    selected_sport = st.selectbox("Choose sport and player to team up with", options=sports_to_pair, index=None, placeholder="select sport - ")
    if selected_sport != st.session_state["selected_sport"]:
        st.session_state["selected_sport"] = selected_sport
        st.session_state["paired_person"] = False
        # st.rerun()

    if selected_sport in all_sports and st.session_state["paired_person"] == False:
        get_player_info = paired_sheet.get_all_records() # check whether player is already registered
        flag_paired = None
        target_row = None
        for idx, row in enumerate(get_player_info):
            if row["SPORTS"] == selected_sport and row["PLAYER1"] == username:
                # st.info(f"You are already paired with {row['PLAYER2']} for {selected_sport}")
                flag_paired = row
                target_row = idx + 2
                break
            elif row["SPORTS"] == selected_sport and row["PLAYER2"] == username:
                # st.info(f"You are already paired with {row['PLAYER1']} for {selected_sport}")
                flag_paired = row
                target_row = idx + 2
                break
       
        if flag_paired:
            partner = [
                {"sport":selected_sport, "Partner Name": flag_paired["PLAYER2"], "Partner Department": flag_paired["DEPARTMENT2"], "Action": "❌ Click to De-pair"}]
            edited = st.data_editor(partner, disabled=["sport", "Partner Name", "Partner Department"], hide_index=True, use_container_width=True, key=f"{selected_sport}_paired", 
                           column_config={"Action":st.column_config.SelectboxColumn("Options", options=["❌ Click to De-pair", "Confirm De-pair"], required=True,)})
            
            editor_state = st.session_state.get(f"{selected_sport}_paired", {})
            edited_rows = editor_state.get("edited_rows", {})
            if edited_rows:
                for row_id, changes in edited_rows.items():
                    if changes.get("Action") == "Confirm De-pair":
                        paired_sheet.delete_rows(start_index = target_row) # delete the paired row from the sheet
                        st.toast("Pairing removed successfully!", icon="🗑️")
                        st.session_state["paired_person"] = False
                        st.success("You have been de-paired successfully!")
                # st.rerun()
                        
        else:
            partner = [
                {"Pair": False, "Name": str(row["NAME"]).strip(), "Department": str(row["DEPARTMENT"]).strip()}
                for row in records 
                if selected_sport in row and str(row[selected_sport]).strip() != ""
            ]
            df = st.data_editor(pd.DataFrame(partner), hide_index=True, disabled=["Name", "Department"], use_container_width=True, key=f"{selected_sport}")
            for idx, row in df.iterrows():
                if row["Pair"]:  # The user clicked the checkbox
                    selected_partner_name = row["Name"]
                    selected_partner_dept = row["Department"]
                    
                    # Append to your Google Sheet
                    paired_sheet.append_row([
                        selected_sport, 
                        username,  
                        department, 
                        selected_partner_name, 
                        selected_partner_dept
                    ])
                    
                    # Save state to hide table, toast a success message, and refresh
                    st.session_state.paired_done = True
                    st.toast(f"Successfully paired with {selected_partner_name}!", icon="✅")
                    st.rerun()
                    break 
 
if __name__ == "__main__":
    selectsports()
