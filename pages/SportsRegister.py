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
PAIRABLE_SPORTS = ["Billiards (Pool)"]
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
        if header not in ("NAME", "DEPARTMENT") and str(row.get(header, "")).strip() == "1"
    ]


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
    row_number, _ = _find_user_row(records, username)

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

    if not logged_in or not username:
        st.error("Please login first.")
        st.stop()

    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.sheet1
    headers = _sheet_headers(worksheet)
    records = worksheet.get_all_records()
    _init_session_state(records, headers, username)

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
            options=SPORT,
            placeholder="Being an audience is not sociable! Select at least one.",
            default=[sport for sport in st.session_state["registered_sports"] if sport in SPORT],
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
    if not current_user_row or str(current_user_row.get(selected_sport, "")).strip() != "1":
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
        if str(row.get(selected_sport, "")).strip() == "1"
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


if __name__ == "__main__":
    selectsports()
