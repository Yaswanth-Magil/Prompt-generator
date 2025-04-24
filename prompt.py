import streamlit as st
import pandas as pd
import io
from tqdm import tqdm
import google.generativeai as genai
import os

# Gemini API key
try:
    API_KEY = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)
    print("API Key loaded successfully from environment variable!")  # Debug print
except KeyError:
    st.error("❌  `GEMINI_API_KEY` environment variable not found. Please configure in GitHub Secrets and Streamlit.")
    st.stop()
except Exception as e:
    st.error(f"❌ An error occurred while loading the API key: {e}")
    st.stop()
  
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Page title
st.title("🍽️ South Indian Dish Prompt Generator")
st.markdown("Upload an Excel file with columns **'dishes'** and **'image description'**. This app will generate AI image prompts for each dish using Gemini.")

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        if "dishes" not in df.columns or "image description" not in df.columns:
            st.error("The Excel file must contain both 'dishes' and 'image description' columns.")
        else:
            st.success("✅ File uploaded and validated!")

            if st.button("⚙️ Generate Prompts"):
                prompts = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, row in tqdm(df.iterrows(), total=len(df)):
                    dish_name = str(row["dishes"])
                    img_desc = str(row["image description"])

                    prompt = f"""
Act as a food stylist and AI prompt engineer.

Generate a highly realistic image prompt for the South Indian dish '{dish_name}'.
The visual setting must follow this image description: {img_desc}

Instructions:
- The dish should be placed on a clean white circular ceramic plate.
- The background must be completely black.
- Use warm, soft directional lighting to bring out the texture and detail.
- Describe the authentic appearance, color, texture, garnishing, and key ingredients of '{dish_name}'.
- Use detailed, cinematic food photography language.
- Keep the response to a single detailed paragraph.

Only return the final image prompt.
"""

                    try:
                        response = model.generate_content(prompt)
                        result = response.text.strip()
                    except Exception as e:
                        result = f"Error: {str(e)}"

                    prompts.append(result)

                    progress = (idx + 1) / len(df)
                    progress_bar.progress(progress)
                    status_text.text(f"Generating prompts: {idx + 1}/{len(df)}")

                df["dish prompt"] = prompts

                # Save to BytesIO
                output = io.BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)

                st.success("🎉 Prompt generation completed!")
                st.download_button(
                    label="📥 Download Result Excel",
                    data=output,
                    file_name="dish_prompts_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"Something went wrong: {e}")
