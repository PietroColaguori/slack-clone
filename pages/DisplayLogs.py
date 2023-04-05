import streamlit as st
import time
from Access import logged_in

if(logged_in()[0]):

    #  Packets to enable firebase DB manipulation  ---
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore

    # Access the database from the current file  ---
    if not firebase_admin._apps:
        cred = credentials.Certificate('credentials.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Create the sidebar with two selectboxes
    with st.sidebar:
        st.title("Display Logs")
        collections = [collection.id for collection in db.collections()]
        collections.remove("Accesso")
        selectedConvo = st.selectbox("Select a conversation:", collections)
        selectedFilter = st.selectbox("Select a filter:", ["Rev. Chronological", "Chronological"])
        selectedUser = st.text_input("Enter the name of a user:")

    # Display the selected options
    st.header(f"Conversation shown: {selectedConvo}")
    st.subheader(f"Filter applied: {selectedFilter}")

    st.markdown("""---""")

    # Get access to the selected collection
    collection_ref = db.collection(selectedConvo)

    # Apply selected filters
    if(selectedFilter == "Chronological"): documents = collection_ref.order_by("timestamp", direction=firestore.Query.ASCENDING).get()
    else: documents = collection_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).get()

    # Cycle through each document and display its data
    for document in documents:
        document_data = document.to_dict()
        if((selectedUser != "" and document_data['sender_name'] == selectedUser) or selectedUser == ''):
            st.write("[" + document_data['sender_name'] + "] " + document_data['message'] + " [" + document_data['timestamp'] + "]\n")

else:
    st.header("Sign In to access the Logs")
