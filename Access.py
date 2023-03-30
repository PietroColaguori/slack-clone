import streamlit as st
import time
import firebase_admin
from firebase_admin import credentials, firestore, storage
import re

# Set icon
st.set_page_config(page_title="MySlack", page_icon="https://cdn3.iconfinder.com/data/icons/social-network-30/512/social-08-512.png")

# Get the client
if not firebase_admin._apps:
    cred = credentials.Certificate('credentials.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Email regex
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Check if username already in use
def user_already_in_use(username):
    docs = db.collection("Accesso").stream()
    for  doc in docs:
            doc_dict = doc.to_dict()
            if(username == doc_dict["username"]): return True
    return False

# Check if email is already in use
def email_already_in_use(email):
    docs = db.collection("Accesso").stream()
    for  doc in docs:
            doc_dict = doc.to_dict()
            if(email == doc_dict["email"]): return True
    return False

# Check if the admin exists
def admin_already_registered(username):
    docs = db.collection("Accesso").stream()
    for  doc in docs:
            doc_dict = doc.to_dict()
            if(doc_dict["isAdmin"] == "True"): return True
    return False

# Manage logged in and admin status
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def logged_in():
    if(st.session_state.logged_in == False):
        st.header("Sign In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        enter = st.button("Sign In")
        if enter:
            docs = db.collection("Accesso").stream()
            for  doc in docs:
                doc_dict = doc.to_dict()
                if username == doc_dict["username"] and password == doc_dict["password"]:
                    st.success("Successfully logged in")
                    st.session_state.logged_in = True
                    #if(doc_dict["isAdmin"] == "True"): 
                        #st.session_state.logged_in[1] = True
            if(not st.session_state.logged_in): st.error("Username or password not correct")
    return st.session_state['logged_in']
     
if(not st.session_state.logged_in):
    # Set up the UI
    choice = st.sidebar.selectbox("Gain Access", ["Sign In", "Sign Up"])

    if(choice == "Sign In"):
        logged_in()

    elif(choice == "Sign Up"):
        st.header("Sign Up")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_repeat = st.text_input("Repeat Password", type="password")
        username = st.text_input("Username")
        checkAdmin = st.checkbox("I am the admin")

        enter = st.button("Sign Up")
        if enter:
            if(checkAdmin): isAdmin = True
            else: isAdmin = False

            validCredentials = True
            if(not is_valid_email(email)):
                st.error("Insert a valid email")
                validCredentials = False
            elif(password != password_repeat):
                st.error("The passwords inserted do not match")
                validCredentials = False
            elif(user_already_in_use(username)):
                st.error("The username " + username + " is already in use")
                validCredentials = False
            elif(email_already_in_use(email)):
                st.error("The email " + email + " is already registered")
                validCredentials = False
            elif(username == '' or email == '' or password == ''):
                st.error("Please fill all the fields")
                validCredentials = False
            elif(isAdmin and admin_already_registered(username)):
                st.error("There is only one admin!")
                validCredentials = False
            elif(validCredentials):
                data = {
                    "username":username,
                    "email":email,
                    "password":password,
                    "isAdmin":str(isAdmin)
                }
                accesso = db.collection("Accesso")
                accesso.document(username).set(data)
                st.success("Successfully registered")
                st.balloons()
            else:
                st.error("An unknown error occurred")

    else:
        st.error("Unkonown error occurred")

else:
    st.header("You are already logged in!")
