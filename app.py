import streamlit as st
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(
    page_title="CFG MongoDB Certificate Generator",
    page_icon="🏅",
    layout="centered"
)

# --- PDF & FONT SETTINGS ---
ORIGINAL_NAME_PLACEHOLDER = "Ritesh Kumar"
PDF_TEMPLATE_PATH = "E-Generated_Certificate.pdf"
FONT_NAME = "tiro"
FONT_SIZE = 30
FONT_COLOR = (0, 0, 0) # Black

# --- HEADER ---
st.title("🎓📄 CFG MongoDB Certificate Generator")
st.write(f"This app will replace the name '{ORIGINAL_NAME_PLACEHOLDER}' in the PDF.")

# --- USER INPUT ---
new_name = st.text_input("Enter the full name for the certificate:", placeholder="e.g., Jane Doe")

if st.button("Generate Certificate ✨", type="primary"):
    if new_name:
        try:
            doc = fitz.open(PDF_TEMPLATE_PATH)
            page = doc[0]

            text_instances = page.search_for(ORIGINAL_NAME_PLACEHOLDER)

            if not text_instances:
                st.error(f"⚠️ Error: Could not find the text '{ORIGINAL_NAME_PLACEHOLDER}' in the PDF.")
            else:
                for inst in text_instances:
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                
                page.apply_redactions()

                rect = text_instances[0]
                
                new_text_len = fitz.get_text_length(new_name, fontname=FONT_NAME, fontsize=FONT_SIZE)
                x_start_point = rect.x0 + (rect.width - new_text_len) / 2
                
                vertical_offset = 5.7
                y_start_point = rect.y1 - vertical_offset

                page.insert_text(
                    (x_start_point, y_start_point),
                    new_name,
                    fontname=FONT_NAME,
                    fontsize=FONT_SIZE,
                    color=FONT_COLOR
                )

                # --- CONVERT TO JPG ---
                pdf_buffer = BytesIO(doc.tobytes())
                doc.close()

                images = convert_from_bytes(pdf_buffer.getvalue())
                
                if images:
                    image = images[0]
                    jpg_buffer = BytesIO()
                    image.save(jpg_buffer, format="JPEG")
                    jpg_buffer.seek(0)

                    # --- DISPLAY AND DOWNLOAD ---
                    st.success("✅ Certificate Generated Successfully!")
                    st.image(jpg_buffer, caption=f"Certificate for {new_name}")
                    st.download_button(
                        label="Download JPG 🖼️",
                        data=jpg_buffer,
                        # FIX: Use .strip() to remove accidental leading/trailing spaces before replacing
                        file_name=f"Certificate_{new_name.strip().replace(' ', '_')}.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error("❌ Could not convert PDF to JPG.")

        except FileNotFoundError:
            st.error(f"🚨 Error: The template file '{PDF_TEMPLATE_PATH}' was not found in the repository.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("⚠️ Please enter a name to generate the certificate.")
