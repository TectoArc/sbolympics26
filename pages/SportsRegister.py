# import streamlit as st
# import gspread
# from google.oauth2.service_account import Credentials
# import pandas as pd
# from main import create_lock
# import time 


# global_lock = create_lock()  # Initialize the lock in session state
# scope = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive"
# ]
# creds = Credentials.from_service_account_info(
#     st.secrets["gcp_service_account"],
#     scopes=scope)

# client = gspread.authorize(creds)

# worksheet= client.open("SBOLYMPICS2026").sheet1

# SPORT = ['Sport Sword', "Trivia Night", "Treasure Hunt", "Dodgeball", "Cricket", "Darts", "Football", "Kho Kho",
#                      "Ping Pong (Table Tennis)", "Basketball", "Volleyball", "Billiards (Pool)", "Backgammon", "Chess", "5k run", "100-m sprint",
#                      "Relay Race", "Cake Baking", "Chill Games (Kids and Adults)", "Badminton"]

# def selectsports():
#     logged_in = st.session_state["logged in"] 
#     username = st.session_state["username"]
#     department = st.session_state["department"]
#     headers = worksheet.row_values(1) # get the list of all headers - includes sports
#     # check whether the user is logged in 
#     if not logged_in :
#         st.error("Please login first")
#         st.stop()

#     # Open page for registration
#     st.set_page_config(page_title="WelcomeToSBOLYMPICS2026", layout="wide")
#     st.title("Welcome", text_alignment='center')
#     # if 'registered_sports' not in st.session_state:
#     #     st.session_state['registered_sports'] = []
#     with st.form("Register"):
#         st.markdown(
#         """
#         <style>
#         .stMultiSelect div[role="listbox"] {
#             max-height: 100px; /* Adjust this height as needed */
#             overflow-y: auto !important;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#         )
#         sports = st.multiselect(label="Which event would you like to participate in ?", options=SPORT, 
#                     placeholder="Being an audiance is not sociable ! Select at least one", 
#                     default=st.session_state['registered_sports'])
#         register = st.form_submit_button("Register")
#         if register:
#             lock_access = global_lock.acquire(timeout=0)
#             if not lock_access:
#                 st.warning("Other players are also registering. Please wait while we process your registration...")
#                 time.sleep(15)
#                 global_lock.acquire(blocking=True)

#             try:
#                 records = worksheet.get_all_records()
#                 cell_updates = []
#                 header_map = {header: idx + 1 for idx, header in enumerate(headers)}  # Map header names to their column indices
#                 user_found = False
#                 target_idx = -1
#                 # check whether the user already exsits in the sheet

#                 for idx, row in enumerate(records, start=2):
#                     if row["NAME"].strip().lower() == username.strip().lower():
#                         user_found = True
#                         target_idx = idx
#                         break # found the user
#                 if user_found:
#                     for s in sports:
#                         # s_header_index = headers.index(s) + 1
#                         if s in header_map:
#                             vals = "1" if s in sports else ""
#                             cell_updates.append({
#                                 "range": gspread.utils.rowcol_to_a1(target_idx, header_map[s]),
#                                 "values": [[vals]]
#                             })
#                         # if s in headers:
#                             # worksheet.update_cell(idx, s_header_index, 1)
#                         st.success(f" {username} registered for {s} successfully!")
#                     # sports_str = ", ".join(sports)
#                     worksheet.batch_update(cell_updates)  # Batch update all the cells at once
#                     # worksheet.update_cell(idx, row[], sports_str)
#                 else:
#                     new_row = {header:"" for header in headers}
#                     new_row["NAME"] = username.strip()
#                     new_row["DEPARTMENT"] = department.strip()
#                     for s in sports:
#                         if s in new_row:
#                             new_row[s] = "1"
#                     new_row_list = [new_row[header] for header in headers]
#                     # Append the new row to the bottom of the sheet
#                     worksheet.append_row(new_row_list)
#                     st.success(f"Successfully created new registration for {username}!")
#             finally:
#                 global_lock.release()
#     if sports not in st.session_state['registered_sports']:
#         st.session_state['registered_sports'] = sports

#     # if register:
#     st.title("Registered Sports", text_alignment='center')
#     st.markdown("For notifications and updates regarding the event, join - (https://chat.whatsapp.com/CNE6qtOU5CPAyB3rvumJaQ)")
#     records = worksheet.get_all_records()
#     player_exists = False
#     player_idx = None
#     for idx, row in enumerate(records, start=2):
#         if row["NAME"].strip().lower() == username.strip().lower():
#             player_exists = True
#             player_idx = idx
#             if len(st.session_state['registered_sports']) == 0:
#                 registered = []
#                 for h in headers:
#                     if h not in ["NAME", "DEPARTMENT"]:
#                         if str(row[h]).strip() == "1":
#                             registered.append(h)
#                 st.session_state['registered_sports'] = registered
#             break

#     if player_exists:
#         cell_updates = []
#         for rs in st.session_state['registered_sports']:
#             c1, c2 = st.columns([0.7, 0.3])
#             with c1:
#                 st.markdown(f"**{rs}**")
#             with c2:
#                 if st.button(f"Delete", key=f"del_{rs}"):
#                     found = False
#                     # records = worksheet.get_all_records()
#                     for idx, row in enumerate(records, start=2):
#                         if row["NAME"].strip().lower() == username.strip().lower():
#                             s_header_index = headers.index(rs) + 1
#                             worksheet.update_cell(idx, s_header_index, "")
#                             st.success(f" {username} de-registered from {rs} successfully!")
#                             st.session_state["registered_sports"].remove(rs)
#                             found = True
#                             break
#                     if found:
#                         st.rerun()
#                     else:
#                         st.error("Record not found")
#     _TeamUP(worksheet, client.open("SBOLYMPICS2026"), username, department)
#     return 

# def _TeamUP(sheet, sheet2, username, department):
#     paired_sheet = sheet2.worksheet("Paired_Sports")
#     sports_to_pair = ["Billiards (Pool)", "Darts"]
#     records = sheet.get_all_records()
#     all_sports = list(records[0].keys())
#     st.title("Pairing")
#     selected_sport = st.selectbox("Choose sport and player to team up with", options=sports_to_pair, index=None, placeholder="select sport - ")
#     if selected_sport != st.session_state["selected_sport"]:
#         st.session_state["selected_sport"] = selected_sport
#         st.session_state["paired_person"] = False
#         # st.rerun()

#     if selected_sport in all_sports and st.session_state["paired_person"] == False:
#         get_player_info = paired_sheet.get_all_records() # check whether player is already registered
#         flag_paired = None
#         target_row = None
#         for idx, row in enumerate(get_player_info):
#             if row["SPORTS"] == selected_sport and row["PLAYER1"] == username:
#                 # st.info(f"You are already paired with {row['PLAYER2']} for {selected_sport}")
#                 flag_paired = row
#                 target_row = idx + 2
#                 break
#             elif row["SPORTS"] == selected_sport and row["PLAYER2"] == username:
#                 # st.info(f"You are already paired with {row['PLAYER1']} for {selected_sport}")
#                 flag_paired = row
#                 target_row = idx + 2
#                 break
       
#         if flag_paired:
#             partner = [
#                 {"sport":selected_sport, "Partner Name": flag_paired["PLAYER2"], "Partner Department": flag_paired["DEPARTMENT2"], "Action": "❌ Click to De-pair"}]
#             edited = st.data_editor(partner, disabled=["sport", "Partner Name", "Partner Department"], hide_index=True, use_container_width=True, key=f"{selected_sport}_paired", 
#                            column_config={"Action":st.column_config.SelectboxColumn("Options", options=["❌ Click to De-pair", "Confirm De-pair"], required=True,)})
            
#             editor_state = st.session_state.get(f"{selected_sport}_paired", {})
#             edited_rows = editor_state.get("edited_rows", {})
#             if edited_rows:
#                 for row_id, changes in edited_rows.items():
#                     if changes.get("Action") == "Confirm De-pair":
#                         paired_sheet.delete_rows(start_index = target_row) # delete the paired row from the sheet
#                         st.toast("Pairing removed successfully!", icon="🗑️")
#                         st.session_state["paired_person"] = False
#                         st.success("You have been de-paired successfully!")
#                 # st.rerun()
                        
#         else:
#             partner = [
#                 {"Pair": False, "Name": str(row["NAME"]).strip(), "Department": str(row["DEPARTMENT"]).strip()}
#                 for row in records 
#                 if selected_sport in row and str(row[selected_sport]).strip() != ""
#             ]
#             df = st.data_editor(pd.DataFrame(partner), hide_index=True, disabled=["Name", "Department"], use_container_width=True, key=f"{selected_sport}")
#             for idx, row in df.iterrows():
#                 if row["Pair"]:  # The user clicked the checkbox
#                     selected_partner_name = row["Name"]
#                     selected_partner_dept = row["Department"]
                    
#                     # Append to your Google Sheet
#                     paired_sheet.append_row([
#                         selected_sport, 
#                         username,  
#                         department, 
#                         selected_partner_name, 
#                         selected_partner_dept
#                     ])
                    
#                     # Save state to hide table, toast a success message, and refresh
#                     st.session_state.paired_done = True
#                     st.toast(f"Successfully paired with {selected_partner_name}!", icon="✅")
#                     st.rerun()
#                     break 
 
# if __name__ == "__main__":
#     selectsports()

import threading
import time

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


try:
    st.set_page_config(page_title="WelcomeToSBOLYMPICS2026", layout="wide")
except st.errors.StreamlitAPIException:
    # If another Streamlit entry point already configured the page, keep going.
    pass


SPREADSHEET_NAME = "SBOLYMPICS2026"
PAIRABLE_SPORTS = ["Billiards (Pool)", "Darts"]
SPORT_CAPS = {
    "Billiards (Pool)": 16,
    "Ping Pong (Table Tennis)": 16,
    "Sport Sword": 16,
    "Darts": 16,
}
SPORT_ALIASES = {
    "Billiards (Pool)": {"Billiards (Pool)", "Billiards", "Pool"},
    "Ping Pong (Table Tennis)": {
        "Ping Pong (Table Tennis)",
        "Ping Pong",
        "Table Tennis",
    },
    "Sport Sword": {"Sport Sword"},
    "Darts": {"Darts"},
}
SPORT = [
    "Sport Sword",
    "Trivia Night",
    "Treasure Hunt",
    "Dodgeball",
    "Cricket",
    "Darts",
    "Football",
    "Kho Kho",
    "Ping Pong (Table Tennis)",
    "Basketball",
    "Volleyball",
    "Billiards (Pool)",
    "Backgammon",
    "Chess",
    "5k run",
    "100-m sprint",
    "Relay Race",
    "Cake Baking",
    "Chill Games (Kids and Adults)",
    "Badminton",
]

global_lock = threading.Lock()


@st.cache_resource(show_spinner=False)
def get_spreadsheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope,
    )
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_NAME)


def _centered_title(text):
    st.markdown(f"<h1 style='text-align: center;'>{text}</h1>", unsafe_allow_html=True)


def _normalize_name(name):
    return str(name or "").strip().lower()


def _normalize_sport_name(name):
    return "".join(char for char in _normalize_name(name) if char.isalnum())


def _is_registered_value(value):
    cleaned = str(value or "").strip().lower()
    return cleaned not in ("", "0", "false", "no")


def _sport_alias_keys(sport):
    aliases = SPORT_ALIASES.get(sport, {sport})
    return {_normalize_sport_name(alias) for alias in aliases}


def _matching_sport_columns(row, sport):
    alias_keys = _sport_alias_keys(sport)
    return [
        column
        for column in row.keys()
        if _normalize_sport_name(column) in alias_keys
    ]


def _row_has_sport_registration(row, sport):
    return any(
        _is_registered_value(row.get(column))
        for column in _matching_sport_columns(row, sport)
    )


def _contains_sport(sports, sport):
    sport_key = _normalize_sport_name(sport)
    return any(_normalize_sport_name(selected_sport) == sport_key for selected_sport in sports)


def _find_user_row(records, username):
    username_key = _normalize_name(username)
    for row_number, row in enumerate(records, start=2):
        if _normalize_name(row.get("NAME")) == username_key:
            return row_number, row
    return None, None


def _registered_sports_from_row(row, headers):
    if not row:
        return []

    return [
        header
        for header in headers
        if header not in ("NAME", "DEPARTMENT") and _is_registered_value(row.get(header))
    ]


def _sport_registration_count(records, sport):
    return sum(1 for row in records if _row_has_sport_registration(row, sport))


def _is_sport_full(records, sport):
    cap = SPORT_CAPS.get(sport)
    return cap is not None and _sport_registration_count(records, sport) >= cap


def _available_sports_for_user(records, registered_sports):
    return [
        sport
        for sport in SPORT
        if _contains_sport(registered_sports, sport) or not _is_sport_full(records, sport)
    ]


def _filter_capped_sports(records, current_registered_sports, selected_sports):
    allowed_sports = []
    capped_sports = []

    for sport in selected_sports:
        if _contains_sport(current_registered_sports, sport) or not _is_sport_full(records, sport):
            allowed_sports.append(sport)
        else:
            capped_sports.append(sport)

    return allowed_sports, capped_sports


def _trivia_team_record(row_number, row_values):
    values = list(row_values) + [""] * max(0, 8 - len(row_values))
    header_values = {"player1", "player2", "player3", "player4"}

    if {_normalize_name(value).replace(" ", "") for value in values[:4]} == header_values:
        return None

    if len(row_values) >= 8:
        players = values[:4]
        departments = values[4:8]
    elif len(row_values) >= 6:
        players = values[1:5]
        departments = str(values[5]).split(", ")
    else:
        players = values[:4]
        departments = values[4:8]

    if not any(str(player).strip() for player in players):
        return None

    record = {"_row_number": row_number}
    for idx in range(4):
        record[f"PLAYER{idx + 1}"] = str(players[idx]).strip()
        department = departments[idx] if idx < len(departments) else ""
        record[f"DEPARTMENT{idx + 1}"] = str(department).strip()

    return record


def _trivia_team_records(trivia_sheet):
    records = []
    for row_number, row_values in enumerate(trivia_sheet.get_all_values(), start=1):
        record = _trivia_team_record(row_number, row_values)
        if record:
            records.append(record)
    return records


def _init_session_state(records, headers, username):
    st.session_state.setdefault("registered_sports", [])
    st.session_state.setdefault("selected_sport", None)
    st.session_state.setdefault("paired_person", False)

    if not st.session_state["registered_sports"]:
        _, user_row = _find_user_row(records, username)
        st.session_state["registered_sports"] = _registered_sports_from_row(user_row, headers)


def _sheet_headers(worksheet):
    headers = worksheet.row_values(1)
    missing_headers = {"NAME", "DEPARTMENT"} - set(headers)
    if missing_headers:
        st.error(f"Missing required sheet header(s): {', '.join(sorted(missing_headers))}")
        st.stop()
    return headers


def _save_registration(worksheet, username, department, selected_sports):
    headers = _sheet_headers(worksheet)
    records = worksheet.get_all_records()
    header_map = {header: idx + 1 for idx, header in enumerate(headers)}
    row_number, user_row = _find_user_row(records, username)
    current_registered_sports = _registered_sports_from_row(user_row, headers)
    selected_sports, capped_sports = _filter_capped_sports(
        records,
        current_registered_sports,
        selected_sports,
    )

    if capped_sports:
        st.warning(
            "Registration is full for: "
            f"{', '.join(capped_sports)}. Those sports were not added."
        )

    if row_number:
        cell_updates = []
        for sport in SPORT:
            if sport in header_map:
                cell_updates.append(
                    {
                        "range": gspread.utils.rowcol_to_a1(row_number, header_map[sport]),
                        "values": [["1" if sport in selected_sports else ""]],
                    }
                )

        if cell_updates:
            worksheet.batch_update(cell_updates)
        st.success(f"Updated registration for {username}.")
    else:
        new_row = {header: "" for header in headers}
        new_row["NAME"] = str(username).strip()
        new_row["DEPARTMENT"] = str(department).strip()

        for sport in selected_sports:
            if sport in new_row:
                new_row[sport] = "1"

        worksheet.append_row([new_row[header] for header in headers])
        st.success(f"Successfully created new registration for {username}.")

    st.session_state["registered_sports"] = list(selected_sports)


def _delete_registration(worksheet, username, sport):
    headers = _sheet_headers(worksheet)
    if sport not in headers:
        st.error(f"Could not find a sheet column for {sport}.")
        return

    records = worksheet.get_all_records()
    row_number, _ = _find_user_row(records, username)
    if not row_number:
        st.error("Record not found.")
        return

    worksheet.update_cell(row_number, headers.index(sport) + 1, "")
    st.session_state["registered_sports"] = [
        registered_sport
        for registered_sport in st.session_state["registered_sports"]
        if registered_sport != sport
    ]
    st.success(f"{username} de-registered from {sport} successfully.")
    st.rerun()


def selectsports():
    logged_in = st.session_state.get("logged in", False)
    username = str(st.session_state.get("username", "")).strip()
    department = str(st.session_state.get("department", "")).strip()

    # if not logged_in or not username:
    #     st.error("Please login first.")
    #     st.stop()

    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.sheet1
    headers = _sheet_headers(worksheet)
    records = worksheet.get_all_records()
    _init_session_state(records, headers, username)
    available_sports = _available_sports_for_user(
        records,
        st.session_state["registered_sports"],
    )

    _centered_title("Welcome")

    with st.form("Register"):
        st.markdown(
            """
            <style>
            .stMultiSelect div[role="listbox"] {
                max-height: 100px;
                overflow-y: auto !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        sports = st.multiselect(
            label="Which event would you like to participate in?",
            options=available_sports,
            placeholder="Being an audience is not sociable! Select at least one.",
            default=[
                sport
                for sport in st.session_state["registered_sports"]
                if sport in available_sports
            ],
        )
        register = st.form_submit_button("Register")

        if register:
            lock_acquired = global_lock.acquire(timeout=0)
            if not lock_acquired:
                st.warning(
                    "Other players are also registering. Please wait while we process your registration..."
                )
                time.sleep(15)
                global_lock.acquire(blocking=True)
                lock_acquired = True

            try:
                _save_registration(worksheet, username, department, sports)
                st.cache_data.clear() 
            finally:
                if lock_acquired:
                    global_lock.release()

    _centered_title("Registered Sports")
    st.markdown(
        "For notifications and updates regarding the event, join "
        "[the WhatsApp group](https://chat.whatsapp.com/CNE6qtOU5CPAyB3rvumJaQ)."
    )

    if st.session_state["registered_sports"]:
        for registered_sport in list(st.session_state["registered_sports"]):
            c1, c2 = st.columns([0.7, 0.3])
            with c1:
                st.markdown(f"**{registered_sport}**")
            with c2:
                if st.button("Delete", key=f"del_{registered_sport}"):
                    lock_acquired = global_lock.acquire(timeout=0)
                    if not lock_acquired:
                        st.warning("Another update is in progress. Please wait...")
                        global_lock.acquire(blocking=True)
                        lock_acquired = True

                    try:
                        _delete_registration(worksheet, username, registered_sport)
                    finally:
                        if lock_acquired:
                            global_lock.release()
    else:
        st.info("You are not registered for any sports yet.")

    _TeamUP(worksheet, spreadsheet, username, department)
    _MultiTeamUP(worksheet, spreadsheet, username, department)


def _TeamUP(sheet, sheet2, username, department):
    paired_sheet = sheet2.worksheet("Paired_Sports")
    records = sheet.get_all_records()
    all_sports = list(records[0].keys()) if records else []

    st.session_state.setdefault("selected_sport", None)
    st.session_state.setdefault("paired_person", False)

    st.title("Pairing")
    selected_sport = st.selectbox(
        "Choose sport and player to team up with",
        options=PAIRABLE_SPORTS,
        index=None,
        placeholder="Select sport",
    )


    if selected_sport != st.session_state["selected_sport"]:
        st.session_state["selected_sport"] = selected_sport
        st.session_state["paired_person"] = False

    if not selected_sport:
        return

    if selected_sport not in all_sports:
        st.warning(f"{selected_sport} is not a column in the registration sheet.")
        return

    _, current_user_row = _find_user_row(records, username)
    if not current_user_row or not _is_registered_value(current_user_row.get(selected_sport)):
        st.info(f"Register for {selected_sport} before choosing a partner.")
        return

    paired_records = paired_sheet.get_all_records()
    existing_pair = None
    target_row = None
    for idx, row in enumerate(paired_records, start=2):
        if row.get("SPORTS") != selected_sport:
            continue

        if _normalize_name(row.get("PLAYER1")) == _normalize_name(username):
            existing_pair = row
            target_row = idx
            break

        if _normalize_name(row.get("PLAYER2")) == _normalize_name(username):
            existing_pair = row
            target_row = idx
            break

    if existing_pair:
        if _normalize_name(existing_pair.get("PLAYER1")) == _normalize_name(username):
            partner_name = existing_pair.get("PLAYER2", "")
            partner_department = existing_pair.get("DEPARTMENT2", "")
        else:
            partner_name = existing_pair.get("PLAYER1", "")
            partner_department = existing_pair.get("DEPARTMENT1", "")

        partner = [
            {
                "Sport": selected_sport,
                "Partner Name": partner_name,
                "Partner Department": partner_department,
                "Action": "Click to De-pair",
            }
        ]
        st.data_editor(
            partner,
            disabled=["Sport", "Partner Name", "Partner Department"],
            hide_index=True,
            use_container_width=True,
            key=f"{selected_sport}_paired",
            column_config={
                "Action": st.column_config.SelectboxColumn(
                    "Options",
                    options=["Click to De-pair", "Confirm De-pair"],
                    required=True,
                )
            },
        )

        editor_state = st.session_state.get(f"{selected_sport}_paired", {})
        edited_rows = editor_state.get("edited_rows", {})
        for changes in edited_rows.values():
            if changes.get("Action") == "Confirm De-pair":
                paired_sheet.delete_rows(start_index=target_row)
                st.session_state["paired_person"] = False
                st.success("You have been de-paired successfully.")
                st.rerun()
        return

    paired_names = {
        _normalize_name(player)
        for row in paired_records
        if row.get("SPORTS") == selected_sport
        for player in (row.get("PLAYER1"), row.get("PLAYER2"))
    }

    partner_options = [
        {
            "Pair": False,
            "Name": str(row.get("NAME", "")).strip(),
            "Department": str(row.get("DEPARTMENT", "")).strip(),
        }
        for row in records
        if _is_registered_value(row.get(selected_sport))
        and _normalize_name(row.get("NAME")) != _normalize_name(username)
        and _normalize_name(row.get("NAME")) not in paired_names
    ]

    if not partner_options:
        st.info("No available partners for this sport yet.")
        return

    df = st.data_editor(
        pd.DataFrame(partner_options),
        hide_index=True,
        disabled=["Name", "Department"],
        use_container_width=True,
        key=f"{selected_sport}",
    )

    for _, row in df.iterrows():
        if not row["Pair"]:
            continue

        selected_partner_name = row["Name"]
        selected_partner_dept = row["Department"]
        lock_acquired = global_lock.acquire(timeout=0)
        if not lock_acquired:
            st.warning("Another pairing update is in progress. Please wait...")
            global_lock.acquire(blocking=True)
            lock_acquired = True

        try:
            paired_sheet.append_row(
                [
                    selected_sport,
                    username,
                    department,
                    selected_partner_name,
                    selected_partner_dept,
                ]
            )
        finally:
            if lock_acquired:
                global_lock.release()

        st.session_state["paired_person"] = True
        st.success(f"Successfully paired with {selected_partner_name}.")
        st.rerun()


def _MultiTeamUP(sheet, sheet2, username, department):
    """
    Handles Trivia Night pairings via a multiselect dropdown.
    Allows user to select 3 registered players and appends their names
    and departments into a single sheet row.
    Expects headerless sheet columns: PLAYER1, PLAYER2, PLAYER3, PLAYER4,
    DEPARTMENT1, DEPARTMENT2, DEPARTMENT3, DEPARTMENT4.
    """
    trivia_sheet = sheet2.worksheet("Trivia_Teams")
    records = sheet.get_all_records()
    
    st.title("Trivia Night Team Registration")

    # 1. Check current user's registration status
    _, current_user_row = _find_user_row(records, username)
    is_registered = current_user_row and _is_registered_value(current_user_row.get("Trivia Night"))

    if not is_registered:
        st.warning("⚠️ You are not registered for Trivia Night yet! Please register in the main tab first.")
        if st.button("🔄 Refresh Registration Status"):
            st.cache_data.clear()
            st.rerun()
        return

    # 2. Fetch current team records to check if user is already teamed up.
    team_records = _trivia_team_records(trivia_sheet)
    user_norm = _normalize_name(username)
    
    existing_team = None
    team_row_idx = None
    
    for row in team_records:
        players = [
            _normalize_name(row.get("PLAYER1", "")),
            _normalize_name(row.get("PLAYER2", "")),
            _normalize_name(row.get("PLAYER3", "")),
            _normalize_name(row.get("PLAYER4", ""))
        ]
        if user_norm in players:
            existing_team = row
            team_row_idx = row["_row_number"]
            break

    # --- CASE A: User already has a team ---
    if existing_team:
        st.subheader("Your Current Team")
        
        # Pull and clean up team member lists
        raw_members = [existing_team.get(f"PLAYER{i}", "") for i in range(1, 5)]
        raw_depts = [existing_team.get(f"DEPARTMENT{i}", "") for i in range(1, 5)]
        
        members_clean = [m for m in raw_members if m.strip()]
        
        for i, member in enumerate(members_clean):
            dept_info = f" ({raw_depts[i]})" if i < len(raw_depts) and raw_depts[i] else ""
            st.write(f"**Player {i+1}:** {member}{dept_info}")

        if st.button("❌ Disband / Leave Team"):
            lock_acquired = global_lock.acquire(timeout=0)
            if not lock_acquired:
                global_lock.acquire(blocking=True)
                lock_acquired = True
            try:
                # Completely remove the row so players can pick new groups
                trivia_sheet.delete_rows(team_row_idx)
                st.success("Team dropped successfully.")
                st.cache_data.clear()
                st.rerun()
            finally:
                if lock_acquired:
                    global_lock.release()
        return

    # --- CASE B: User creating a team ---
    # Find everyone already assigned to a team to prevent double-pairing
    taken_players = {
        _normalize_name(row.get(f"PLAYER{i}", ""))
        for row in team_records
        for i in range(1, 5)
        if row.get(f"PLAYER{i}", "")
    }

    # Map available registered players from the main registration sheet
    # Excludes the current user and anyone already on a trivia team
    available_partners = {}
    for row in records:
        r_name = str(row.get("NAME", "")).strip()
        r_dept = str(row.get("DEPARTMENT", "")).strip()
        r_norm = _normalize_name(r_name)
        
        if _is_registered_value(row.get("Trivia Night")):
            if r_norm != user_norm and r_norm not in taken_players and r_name:
                # Storing their department matched to their name
                available_partners[r_name] = r_dept

    st.subheader("Build Your Trivia Team")
    st.info("Choose exactly **3 teammates** to complete your 4-person squad.")

    # Multiselect input for player list selection
    selected_names = st.multiselect(
        "Choose Teammates:",
        options=list(available_partners.keys()),
        max_selections=3,
        placeholder="Select players..."
    )

    if st.button("🚀 Register Team"):
        if len(selected_names) != 3:
            st.error("Please choose exactly 3 teammates before registering your Trivia Night team.")
            return

        # The user is always Player 1
        final_players = [username] + selected_names
        final_depts = [department] + [available_partners[name] for name in selected_names]

        row_to_append = final_players + final_depts

        lock_acquired = global_lock.acquire(timeout=0)
        if not lock_acquired:
            st.warning("Database busy, holding request...")
            global_lock.acquire(blocking=True)
            lock_acquired = True

        try:
            latest_team_records = _trivia_team_records(trivia_sheet)
            latest_taken_players = {
                _normalize_name(row.get(f"PLAYER{i}", ""))
                for row in latest_team_records
                for i in range(1, 5)
                if row.get(f"PLAYER{i}", "")
            }
            selected_norms = {_normalize_name(name) for name in selected_names}
            unavailable_players = selected_norms & latest_taken_players

            if user_norm in latest_taken_players:
                st.error("You are already part of a Trivia Night team. Refresh the page to view it.")
                st.cache_data.clear()
                return

            if unavailable_players:
                unavailable_names = [
                    name
                    for name in selected_names
                    if _normalize_name(name) in unavailable_players
                ]
                st.error(
                    "The following teammate(s) are no longer available: "
                    f"{', '.join(unavailable_names)}. Please choose again."
                )
                st.cache_data.clear()
                return

            trivia_sheet.append_row(row_to_append)
            st.success("🎉 Team registered successfully!")
            st.cache_data.clear()
            st.rerun()
        finally:
            if lock_acquired:
                global_lock.release()

    # """
    # Handles multi-person pairings (e.g., Trivia Night) where a team 
    # consists of up to 4 players total (User + up to 3 teammates).
    # Expects sheet columns: DEPARTMENT, PLAYER1, PLAYER2, PLAYER3, PLAYER4
    # """
    # trivia_sheet = sheet2.worksheet("Trivia_Teams")
    # records = sheet.get_all_records()
    
    # st.title("Trivia Night Team Registration")

    # # 1. Verify user is registered for Trivia in the main sheet
    # _, current_user_row = _find_user_row(records, username)
    # if not current_user_row or str(current_user_row.get("Trivia", "")).strip() != "1":
    #     st.info("Register for Trivia Night !")
    #     return

    # # 2. Fetch current team data
    # team_records = trivia_sheet.get_all_records()
    # user_norm = _normalize_name(username)
    
    # # 3. Check if user is already in a team
    # existing_team = None
    # team_row_idx = None
    
    # for idx, row in enumerate(team_records, start=2): # Row 1 is header
    #     players = [
    #         _normalize_name(row.get("PLAYER1", "")),
    #         _normalize_name(row.get("PLAYER2", "")),
    #         _normalize_name(row.get("PLAYER3", "")),
    #         _normalize_name(row.get("PLAYER4", ""))
    #     ]
    #     if user_norm in players:
    #         existing_team = row
    #         team_row_idx = idx
    #         break

    # # --- CASE A: User is already in a team (View / Leave Management) ---
    # if existing_team:
    #     st.subheader(f"Your Team ({existing_team.get('DEPARTMENT', 'Unknown Department')})")
        
    #     # Display current team members
    #     members = [existing_team.get(f"PLAYER{i}", "") for i in range(1, 5)]
    #     members_clean = [m for m in members if m.strip()]
        
    #     for i, member in enumerate(members_clean, 1):
    #         st.write(f"**Member {i}:** {member}")

    #     # Drop/Leave team feature
    #     if st.button("Leave Team"):
    #         lock_acquired = global_lock.acquire(timeout=0)
    #         if not lock_acquired:
    #             st.warning("Database busy, retrying...")
    #             global_lock.acquire(blocking=True)
    #             lock_acquired = True
            
    #         try:
    #             # Find which position the user occupies and clear it
    #             updated_row = list(existing_team.values())
    #             for i in range(1, 5):
    #                 if _normalize_name(existing_team.get(f"PLAYER{i}", "")) == user_norm:
    #                     # Clear player cell in sheet (adjusting index for 1-based gspread columns)
    #                     # Expecting Order: Department (Col 1), Player1 (Col 2)...
    #                     trivia_sheet.update_cell(team_row_idx, i + 1, "")
    #                     break
                
    #             # Clean up empty rows if everyone left
    #             latest_row_vals = trivia_sheet.row_values(team_row_idx)[1:] # Skip department
    #             if not any(latest_row_vals):
    #                 trivia_sheet.delete_rows(team_row_idx)
                    
    #             st.success("You have left the team.")
    #             st.rerun()
    #         finally:
    #             if lock_acquired:
    #                 global_lock.release()
    #     return

    # # --- CASE B: User is not in a team (Join or Create) ---
    # # Find all users already assigned to a team to exclude them from choices
    # taken_players = {
    #     _normalize_name(row.get(f"PLAYER{i}", ""))
    #     for row in team_records
    #     for i in range(1, 5)
    #     if row.get(f"PLAYER{i}", "")
    # }

    # st.subheader("Join an Existing Team or Create a New One")
    
    # # Format available spots in existing department teams
    # open_teams = []
    # for idx, row in enumerate(team_records, start=2):
    #     team_players = [row.get(f"PLAYER{i}", "") for i in range(1, 5) if row.get(f"PLAYER{i}", "")]
    #     if len(team_players) < 4:
    #         open_teams.append({
    #             "RowIndex": idx,
    #             "Department": row.get("DEPARTMENT", ""),
    #             "Current Members": ", ".join(team_players),
    #             "Spots Left": 4 - len(team_players),
    #             "Join": False
    #         })

    # # Display open teams
    # if open_teams:
    #     st.write("### Available Teams to Join:")
    #     df_teams = st.data_editor(
    #         pd.DataFrame(open_teams),
    #         hide_index=True,
    #         disabled=["Department", "Current Members", "Spots Left"],
    #         use_container_width=True,
    #         key="open_trivia_teams"
    #     )
        
    #     for _, row in df_teams.iterrows():
    #         if row["Join"]:
    #             target_row = row["RowIndex"]
                
    #             lock_acquired = global_lock.acquire(timeout=0)
    #             if not lock_acquired:
    #                 global_lock.acquire(blocking=True)
    #                 lock_acquired = True
                
    #             try:
    #                 # Refetch row to verify it didn't fill up while viewing
    #                 current_row_vals = trivia_sheet.row_values(target_row)
    #                 # gspread row_values drops trailing empty cells; pad it to length 5
    #                 while len(current_row_vals) < 5:
    #                     current_row_vals.append("")
                        
    #                 # Find first empty slot (columns 2 to 5)
    #                 inserted = False
    #                 for col_idx in range(2, 6):
    #                     if not current_row_vals[col_idx - 1].strip():
    #                         trivia_sheet.update_cell(target_row, col_idx, username)
    #                         inserted = True
    #                         break
                    
    #                 if inserted:
    #                     st.success("Successfully joined the team!")
    #                     st.rerun()
    #                 else:
    #                     st.error("Team filled up right before you clicked! Please choose another.")
    #             finally:
    #                 if lock_acquired:
    #                     global_lock.release()

    # # Option to establish a completely brand new team
    # st.write("---")
    # st.write("### Can't find a team?")
    # if st.button("Create a New Team for Your Department"):
    #     lock_acquired = global_lock.acquire(timeout=0)
    #     if not lock_acquired:
    #         global_lock.acquire(blocking=True)
    #         lock_acquired = True
            
    #     try:
    #         # Append new row: Department, User (Player 1), empty space for remaining 3 slots
    #         trivia_sheet.append_row([department, username, "", "", ""])
    #         st.success(f"New team created for {department}! Others can now join you.")
    #         st.rerun()
    #     finally:
    #         if lock_acquired:
    #             global_lock.release()


if __name__ == "__main__":
    selectsports()
