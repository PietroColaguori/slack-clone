import firebase_admin
from firebase_admin import credentials, firestore, storage
import streamlit as st
from Access import logged_in

if(logged_in()[0]):
    
    # Access the database
    if not firebase_admin._apps:
        cred = credentials.Certificate('credentials.json')
        firebase_admin.initialize_app(cred, {'StorageBucket':'myslack-9f623.appspot.com'})
    db = firestore.client()

    # Get contents of the bucket
    bucket = storage.bucket('myslack-9f623.appspot.com')
    blobs = bucket.list_blobs()
    blob_list = [blob.name for blob in blobs]

    # Create UI
    st.subheader('List of Files:')
    if not blob_list:
        st.write('No files found in the bucket.')
    else:
        selected_file = st.selectbox('Select a file to download', blob_list)
        st.write(f'You selected: {selected_file}')

    # Button to download file
    blob = bucket.blob(selected_file) 
    blob_content = blob.download_as_string()
    st.download_button(label="Scarica", data=blob_content, file_name=selected_file, mime='application/octet-stream')

else:
    st.header("Login to download content")
