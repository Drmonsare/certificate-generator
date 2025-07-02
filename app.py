import streamlit as st
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Certificate Generator",
    page_icon="✅",
    layout="centered"
)

# --- PDF & FONT SETTINGS ---
# Set the placeholder to the exact name found in your PDF
ORIGINAL_NAME_PLACEHOLDER = "Ritesh Kumar"
PDF_TEMPLATE_PATH = "E-Generated_Certificate.pdf"
FONT_NAME = "helv"  # Using a standard font like Helvetica
FONT_SIZE = 30      # Adjust font size as needed
FONT_COLOR = (0, 0, 0) # Black

# --- HEADER ---
st.title("📜 Certificate Generator")
st.write(f"This app will replace the name '{ORIGINAL_NAME_PLACEHOLDER}' in the PDF.")

# --- USER INPUT ---
new_name = st.text_input("Enter the full name for the certificate:", placeholder="e.g., Jane Doe")

if st.button("Generate Certificate ✨", type="primary"):
    if new_name:
        try:
            # Open the PDF template
            doc = fitz.open(PDF_TEMPLATE_PATH)
            page = doc[0]

            # Find all instances of the placeholder text
            text_instances = page.search_for(ORIGINAL_NAME_PLACEHOLDER)

            if not text_instances:
                st.error(f"⚠️ Error: Could not find the text '{ORIGINAL_NAME_PLACEHOLDER}' in the PDF. Check for typos.")
            else:
                # Erase the placeholder text by adding a white redaction rectangle
                for inst in text_instances:
                    page.add_redact_annot(inst, fill=(1, 1, 1)) # Fill with white
                
                # Apply the redactions to permanently remove the old text
                page.apply_redactions()

                # --- Add the new name, centered ---
                # We use the position of the first found instance
                rect = text_instances[0] 
                
                # Calculate where to insert the new text to be centered
                new_text_len = fitz.get_text_length(new_name, fontname=FONT_NAME, fontsize=FONT_SIZE)
                x_start_point = rect.x0 + (rect.width - new_text_len) / 2
                
                # The y-coordinate should be the baseline of the original text's box
                y_start_point = rect.y1 

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
                        file_name=f"Certificate_{new_name.replace(' ', '_')}.jpg",
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
