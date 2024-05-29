import streamlit as st
import pandas as pd
import xlsxwriter
import requests
from io import BytesIO

# Access details for bot
CIL_LOGIN_URL = 'https://appadmin.cilantro.cafe/authpanel/login/checklogin'
CIL_BEANS_URL = 'https://appadmin.cilantro.cafe/authpanel/coine/editcoine'
CIL_EMAIL = "admin@cilantro.com"
CIL_PASSWORD = "admin@123"

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4515.107 Safari/537.36"
}

# Create a session object
session = requests.Session()

# Function to log in and maintain the session
def login():
    session.get(url=CIL_LOGIN_URL, headers=HEADER)
    payload = {
        "email": CIL_EMAIL,
        "password": CIL_PASSWORD,
        "timezone": "Africa/Cairo"
    }
    login_response = session.post(url=CIL_LOGIN_URL, data=payload, headers=HEADER)
    if "Invalid email or password" in login_response.text:
        return False
    else:
        return True

# Function to add beans
def addbeans(custid, ncoins):
    payload = {
        "modeluser_id": custid,
        "modal_username": "",
        "model_transactiontype": "Credited",
        "model_transactioncoine": ncoins,
        "model_transactiondescriptions": "This is an automated bean adjustment"
    }
    create_notif_response = session.post(url=CIL_BEANS_URL, data=payload, headers=HEADER, allow_redirects=False)
    if create_notif_response.status_code == 303:
        redirect_url = create_notif_response.headers['Location']
        create_notif_response = session.get(redirect_url, headers=HEADER)
    return create_notif_response.status_code, create_notif_response.text

# Streamlit app
st.title('Beans Adjustment Tool')

# Provide a template for users to download
st.header('Download Template')
template_data = {
    'userid': [1860, 1860],
    'beans': [3000, 1500]
}
template_df = pd.DataFrame(template_data)
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    template_df.to_excel(writer, index=False)
buffer.seek(0)
st.download_button(label="Download Template", data=buffer, file_name='template.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Upload Excel file
st.header('Upload Excel File')
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write(df)

    if login():
        st.success('Logged in successfully')
        for index, row in df.iterrows():
            custid = row['userid']
            ncoins = row['beans']
            status_code, response_text = addbeans(custid, ncoins)
            if status_code == 200:
                st.success(f"Beans added successfully to {custid}.")
            else:
                st.error(f"Error adding beans to {custid}: {status_code} - {response_text}")
    else:
        st.error('Login failed')
