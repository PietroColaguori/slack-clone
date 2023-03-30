import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
from Access import logged_in

if(logged_in()):

    # Get Firebase app and Firestore client
    firebase_app = firebase_admin.get_app()
    db = firestore.client(app=firebase_app)

    # Implement CREATE CHANNEL
    new_channel = st.text_input("New channel name:")
    if(st.button("Create channel")):
        if not new_channel:
            st.warning("Please enter a name for the new channel")
        else:
            new_collection_ref = db.collection(new_channel)
            docName = "Dummy"
            initial_data = {"dummy":"dummy"}
            new_collection_ref.document(docName).set(initial_data)
            st.success("New channel " + new_channel + " created!")

            st.experimental_rerun()

    # Implement DELETE CHANNEL
    target_channel = st.text_input("Channel you want to delete [!]")
    if(st.button("Delete channel")):
        if(not target_channel):
         st.warning("PLease enter a name for the target channel")
        else:
            # Delete collection from DB
            docs = db.collection(target_channel).stream()
            for doc in docs:
                doc.reference.delete()
            db.collection(target_channel).document().delete()

            # st.session_state.collections.remove(target_channel) !!!

            st.success("Channel " + target_channel + " deleted!")

            st.experimental_rerun()

else:
    st.header("Only the Admin can access this page!")
    st.subheader("If you are the Admin, please Sign In first")
