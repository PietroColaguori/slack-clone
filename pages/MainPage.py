import streamlit as st
import pandas as pd
import numpy as np
import time

#  Packets to enable firebase DB manipulation  ---
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

from Access import logged_in
      
# Access the database from the current file  ---

if not firebase_admin._apps:
    cred = credentials.Certificate('credentials.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Title of Page
st.title("Slack Clone")

if(logged_in()):

    # Application header
    st.header("Welcome, Pietro")

    # Retrieve data from DB
    collection_names = [collection.id for collection in db.collections()] #!!!
    if "collections" not in st.session_state:
        st.session_state.collections = collection_names

    if("Accesso" in st.session_state.collections): st.session_state.collections.remove("Accesso")

    # keys -> sections, lists -> radio options
    options_dict = {'Channels': st.session_state.collections, 'Messages': ['Chiara Iannicelli', 'Karen Kolendowska', 'Lorenzo Colombini']}

    # Manage a buffer for each convo by using a dictionary
    convo_dict = {'General':"", 'IT':"", 'Sales':"", 'Social':"", 'Legal':"", 'HR':"", 'Chiara Iannicelli':"", 'Karen Kolendowska':"", 'Lorenzo Colombini':""}

    # Add channels and directs to session state
    if "channels_dms" not in st.session_state:
        st.session_state.channels_dms = options_dict

    # Add log of messages to session state
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = convo_dict

    # Select a section to start with
    selected_section = st.sidebar.selectbox("Choose section:", sorted(st.session_state.channels_dms.keys()))

    # Select conversation from radio
    selected_convo = st.sidebar.radio("Choose conversation:", sorted(st.session_state.channels_dms.get(selected_section)))

    # Add selector to session state
    if "selected" not in st.session_state:
        st.session_state.selected = selected_section

    # Add radio bar to session state
    if "radio_bar" not in st.session_state:
        st.session_state.radio_bar = selected_convo

    # Create a bucket for file uploading
    bucket = storage.bucket("myslack-9f623.appspot.com")

    # Creating form -> main panel of application
    with st.form("send_msg", clear_on_submit = True):

        # Show current channel/personal chat
        st.subheader(f"Selection: {selected_convo}")

        # Input to enable message sending
        new_message = st.text_input("Insert your message")

        # Button to upload a file
        uploaded_file = st.file_uploader("Upload a file")

        # Button to send string
        send_btn = st.form_submit_button("Send")

        # Get access to the selected collection
        collection_ref = db.collection(selected_convo)
        documents = collection_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).get()

        # On button click do
        if send_btn:
            # Check for errors
            if(new_message == '' and uploaded_file is None): st.warning("Please insert your message")
            elif(uploaded_file is None):
                # Add message to the convo including the hour and minute
                user_input = new_message
                new_message += " [" + time.strftime("%H:%M") + time.strftime(" - %d/%m/%Y") + "]\n"
                st.write(new_message, "\n")

                # Create dictionary to store message data
                # | _messaggio_ | mittente | timestamp |
                timestamp = time.strftime("%Y/%m/%d - %H:%M:%S")
                message_data = {
                    "message":user_input,
                    "sender_name":"altroNome",
                    "timestamp":timestamp
                }

                # Add the message to the firestore collection
                collection_ref = db.collection(selected_convo)
                docName = "msg" + time.strftime("%Y/%m/%d - ") + time.strftime("%H:%M:%S")
                collection_ref.document(docName).set(message_data)

            else:
                blob = bucket.blob(uploaded_file.name)
                blob.upload_from_string(uploaded_file.read())

                new_message = "Uploaded the file: " + uploaded_file.name
                message = new_message
                new_message += " [" + time.strftime("%H:%M") + time.strftime(" - %d/%m/%Y") + "]\n"
                st.write(new_message, "\n")

                timestamp = time.strftime("%Y/%m/%d - %H:%M:%S")
                #timestamp = time.strftime("%Y:%m:%d:%H:%M:%S")
                message_data = {
                    "message":message,
                    "sender_name":"altroNome",
                    "timestamp":timestamp
                }

                collection_ref = db.collection(selected_convo)
                docName = "msg" + time.strftime("%Y:%m:%d - ") + time.strftime("%H:%M:%S")
                collection_ref.document(docName).set(message_data)

                st.success("File uploaded successfully")

            st.experimental_rerun()

    # Display della chat
    with st.form("displayChat"):
        clear_btn = st.form_submit_button("Clear", disabled=True)
        collection_ref = db.collection(selected_convo)
        documents = collection_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).get()
        for document in documents:
                document_data = document.to_dict()
                st.write("[" + document_data['sender_name'] + "] " + document_data['message'] + " [" + document_data['timestamp'] + "]\n")

else:
    st.header("Sign In to visualize your Home Page")
