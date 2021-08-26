import base64
from time import gmtime, strftime
from urllib.parse import urlsplit

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from stqdm import stqdm

STYLE = """
<style>
img {
    max-width: 100%;
}
</style>
"""

FILE_TYPES = ["csv"]


def check_backlink(url, backlink):
    request = requests.get(url)
    if request.ok:
        raw = request.text
        soup = BeautifulSoup(raw, "html.parser")
        anchors = soup.find_all('a')  # find all anchor tag
        flag = False
        herf_same = []
        for anchor in anchors:
            herf = anchor.attrs.get('href')
            try:
                if urlsplit(herf).netloc == urlsplit(backlink).netloc:
                    herf_same.append(herf)
            except:
                pass
            if herf == backlink:  # extract herf link and compare
                flag = True
        for e in herf_same:
            if backlink in e:
                flag = True
        return flag, herf_same
    else:
        return False, []


def status_code(list_):
    status_ = []
    for i in list_:
        if i:
            try:
                request = requests.get(i, timeout=60)
                status_.append(request.status_code)
            except:
                status_.append(404)
        else:
            status_.append(None)
    return status_


def check(data):
    status = []
    Links = []
    for index, info in stqdm(data.iterrows(), total=len(data)):
        try:
            stat, links = check_backlink(info['AWU'], info['BU'])
            status.append(stat)
            links += [None] * (5 - len(links))
            Links.append(links)
        except:
            status.append('No')
            Links.append([None] * 5)
    data['Time-Initiation'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    data['Brand URLs Present'] = status
    data['Brand URLs Present'] = data['Brand URLs Present'].apply(lambda x: 'Yes' if x else 'No')
    data['AWU http response code'] = status_code(data['AWU'].tolist())
    data = data[['Time-Initiation', 'BU', 'AWU', 'Brand URLs Present', 'AWU http response code']]
    l1 = []
    l2 = []
    l3 = []
    l4 = []
    l5 = []
    for _l1, _l2, _l3, _l4, _l5 in stqdm(Links, total=len(Links)):
        l1.append(_l1)
        l2.append(_l2)
        l3.append(_l3)
        l4.append(_l4)
        l5.append(_l5)
    data['Brand URLs 1'] = l1
    data['Brand URLs 1 http response code'] = status_code(l1)
    data['Brand URLs 2'] = l2
    data['Brand URLs 2 http response code'] = status_code(l2)
    data['Brand URLs 3'] = l3
    data['Brand URLs 3 http response code'] = status_code(l3)
    data['Brand URLs 4'] = l4
    data['Brand URLs 4 http response code'] = status_code(l4)
    data['Brand URLs 5'] = l5
    data['Brand URLs 5 http response code'] = status_code(l5)
    return data


def download(text):
    text = text.encode()
    b64 = base64.b64encode(text).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv" target="_blank">Download</a>'
    return href


def main():
    st.markdown(f"""# `Backlink`""", unsafe_allow_html=True)
    st.markdown(STYLE, unsafe_allow_html=True)
    file = st.file_uploader("Upload file", type=FILE_TYPES)
    if st.button('check'):
        try:
            data = pd.read_csv(file)
            data = check(data)
            st.success('success')
            st.dataframe(data.head())
            st.markdown(download(data.to_csv(index=False)), unsafe_allow_html=True)
            file.close()
        except Exception as e:
            _ = e


if __name__ == "__main__":
    st.markdown("""
                    <style>
                    footer {visibility: hidden;}
                    #MainMenu {visibility: hidden;}
                    </style>
                    """, unsafe_allow_html=True)
    main()
