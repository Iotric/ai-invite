import streamlit as st

# Initialize session state for dynamic text boxes
if "text_boxes" not in st.session_state:
    st.session_state.text_boxes = ["Default Text"]  # Start with one default text box

st.title("Dynamic Form with Addable Text Boxes")

# Function to add a new text box
def add_text_box():
    st.session_state.text_boxes.append("New Text")

# Render text boxes dynamically
st.write("Fill out the text boxes below:")
for i, text in enumerate(st.session_state.text_boxes):
    st.session_state.text_boxes[i] = st.text_input(
        label=f"Text Box {i+1}",
        value=text,
        key=f"text_box_{i}"
    )

# Add a button to add new text boxes
st.button("Add Text Box", on_click=add_text_box)

# Submit button to process the inputs
if st.button("Submit"):
    st.success("Form submitted successfully!")
    st.write("Here are your inputs:")
    st.json(st.session_state.text_boxes)
