import streamlit as st
import base64
import os
from openai import OpenAI
from PIL import Image
from io import BytesIO

# Initialize OpenAI client
client = OpenAI()

# Set Streamlit page config
st.set_page_config(page_title="AI Nail Art Generator", layout="centered")

st.title("💅 AI Nail Art Generator")
st.markdown("Upload a photo of your hand and describe the nail art style you want to try!")

# File uploader
uploaded_file = st.file_uploader("Upload your hand image", type=["jpg", "jpeg", "png"])

# Style prompt
style_prompt = st.text_input("Enter the nail art style (e.g., 'floral pastel', 'galaxy theme', 'minimal French tips')")

# Generate button
if st.button("Generate Nail Art") and uploaded_file and style_prompt:
    with st.spinner("Generating your nail art..."):

        # Save uploaded image temporarily
        with open("temp_hand_image.png", "wb") as f:
            f.write(uploaded_file.read())

        # Construct the full prompt
        full_prompt = f"""
        You are a professional nail artist and image editor. Your task is to analyze the uploaded image, carefully identify the fingers and fingernails, and apply realistic and beautifully styled nail art in the style of: {style_prompt}.

        Ensure the nail art aligns perfectly with the shape, size, and orientation of each nail. Maintain the original lighting and shadows of the hand to make the result appear photorealistic and natural.

        Avoid any misplacement, missing edges, or unrealistic overlays. The final image should look like an unedited photo of a real hand with professionally done nail art in the requested style.
        """

        try:
            # Call OpenAI image edit API
            result = client.images.edit(
                model="gpt-image-1",
                image=[open("temp_hand_image.png", "rb")],
                prompt=full_prompt,
            )

            # Decode image result
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            generated_image = Image.open(BytesIO(image_bytes))

            # Display result
            st.image(generated_image, caption="🎨 AI-Generated Nail Art", use_column_width=True)

            # Option to download
            st.download_button(
                label="Download Image",
                data=image_bytes,
                file_name="nail_art_result.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
        finally:
            # Clean up
            if os.path.exists("temp_hand_image.png"):
                os.remove("temp_hand_image.png")
else:
    st.info("👆 Upload a hand image and type a nail art prompt to start.")

