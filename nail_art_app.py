import streamlit as st
import base64
import os
from openai import OpenAI
from PIL import Image
from io import BytesIO

# Initialize OpenAI client
client = OpenAI()

# Function to encode the uploaded image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to check image quality with GPT-4 Vision
def validate_hand_image(base64_image):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": "Is this image clearly showing a human hand with visible fingernails in good lighting? Respond with 'yes' or 'no' and explain why briefly." },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"error: {e}"

# Set Streamlit config
st.set_page_config(page_title="AI Nail Art Generator", layout="centered")
st.title("💅 AI Nail Art Generator")
st.markdown("Upload a clear photo of your hand and describe the nail art style you want to try!")

# Upload input
uploaded_file = st.file_uploader("Upload your hand image", type=["jpg", "jpeg", "png"])
style_prompt = st.text_input("Enter the nail art style (e.g., 'floral pastel', 'galaxy theme', 'minimal French tips')")

# Generate button
if st.button("Generate Nail Art") and uploaded_file and style_prompt:
    with st.spinner("Validating your image..."):

        # Save uploaded image temporarily
        temp_image_path = "temp_hand_image.png"
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_file.read())

        # Validate image using GPT-4 Vision
        base64_image = encode_image(temp_image_path)
        validation_feedback = validate_hand_image(base64_image)

        if validation_feedback.lower().startswith("yes"):
            st.success("👍 Your hand photo looks great! Let’s work our nail art magic...")

            # Construct the nail art prompt
            full_prompt = f"""
            You are a professional nail artist and image editor. Your task is to analyze the uploaded image, carefully identify the fingers and fingernails, and apply realistic and beautifully styled nail art in the style of: {style_prompt}.

            Ensure the nail art aligns perfectly with the shape, size, and orientation of each nail. Maintain the original lighting and shadows of the hand to make the result appear photorealistic and natural.

            Avoid any misplacement, missing edges, or unrealistic overlays. The final image should look like an unedited photo of a real hand with professionally done nail art in the requested style.
            """

            with st.spinner("Generating your nail art..."):
                try:
                    result = client.images.edit(
                        model="gpt-image-1",
                        image=[open(temp_image_path, "rb")],
                        prompt=full_prompt,
                    )

                    image_base64 = result.data[0].b64_json
                    image_bytes = base64.b64decode(image_base64)
                    generated_image = Image.open(BytesIO(image_bytes))

                    st.image(generated_image, caption="🎨 AI-Generated Nail Art", use_column_width=True)

                    st.download_button(
                        label="Download Image",
                        data=image_bytes,
                        file_name="nail_art_result.png",
                        mime="image/png"
                    )

                except Exception as e:
                    st.error(f"❌ Error generating nail art: {e}")
        else:
            st.warning("⚠️ Your hand image may not be suitable for nail art generation.")
            st.info(f"💬 Feedback: {validation_feedback}")
            st.info("Please re-upload a clear image of your hand with well-lit, visible fingernails.")

        # Clean up
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

else:
    st.info("👆 Upload a hand image and type a nail art prompt to start.")
