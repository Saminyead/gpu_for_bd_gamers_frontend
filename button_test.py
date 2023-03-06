import streamlit as st

input_num = st.number_input(label="Double your investment here! (Obviously not a scam lol)")

def double_number(some_number=input_num):
    st.write(some_number * 2)

is_input_num = bool(input_num)
st.write(f"input_num state = {is_input_num}")

input_btn = st.button(label="Click Me")
is_input_btn = bool(input_btn)
st.write(f"input_btn state = {is_input_btn}")

if input_num or input_btn:
    double_number()