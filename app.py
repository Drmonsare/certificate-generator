import streamlit as st
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import os
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Certificate Generator",
    page_icon="✅",
    layout="centered"
)

# --- IMPORTANT ---
# Change this to the exact placeholder text in your PDF template.
ORIGINAL_NAME_PLACEHOLDER = "Ritesh Kumar"
PDF_TEMPLATE_PATH = "E-Generated_Certificate.pdf"
FONT_NAME = "helv" # Helvetica
FONT_SIZE = 26
FONT_COLOR = (0, 0, 0) # Black

# --- HEADER ---
st.title("📜 Certificate Generator")
st.write("Enter your full name below to generate your personalized certificate.")

# --- USER INPUT ---
new_name = st.text_input("Enter your full name:", placeholder="e.g., Jane Doe")

if st.button("Generate Certificate ✨", type="primary"):
    if new_name:
        try:
            # --- PDF PROCESSING ---
            # Open the PDF template
            doc = fitz.open(PDF_TEMPLATE_PATH)
            page = doc[0]

            # Find the rectangle of the placeholder text
            text_instances = page.search_for(ORIGINAL_NAME_PLACEHOLDER)

            if not text_instances:
                st.error(f"⚠️ Placeholder text '{ORIGINAL_NAME_PLACEHOLDER}' not found in the PDF. Please check the `ORIGINAL_NAME_PLACEHOLDER` variable in the script.")
            else:
                # Erase the old text by adding a white redaction rectangle
                for inst in text_instances:
                    page.add_redact_annot(inst, fill=(1, 1, 1)) # Fill with white
                
                page.apply_redactions() # Apply the redaction

                # Add the new name, centered in the first placeholder's area
                # You may need to adjust the y-coordinate (+28.35 in your code) for perfect alignment
                rect = text_instances[0]
                
                # Calculate the starting point to center the new text
                new_text_len = fitz.get_text_length(new_name, fontname=FONT_NAME, fontsize=FONT_SIZE)
                x_start = rect.x0 + (rect.width - new_text_len) / 2
                
                page.insert_text(
                    (x_start, rect.y0 + 28.35), # Adjust y-coordinate as needed
                    new_name,
                    fontname=FONT_NAME,
                    fontsize=FONT_SIZE,
                    color=FONT_COLOR
                )

                # --- CONVERT TO JPG ---
                # Save the modified PDF to a memory buffer
                pdf_buffer = BytesIO(doc.save())
                doc.close()
                pdf_buffer.seek(0)

                # Convert the first page of the PDF buffer to a JPG image
                images = convert_from_path(None, poppler_path=None, first_page=1, last_page=1, fmt='jpeg', userpw=None, use_cropbox=False, strict=False, thread_count=1, output_folder=None, single_file=True, paths_only=False, pdf_file=pdf_buffer.getvalue())
                
                if images:
                    image = images[0]
                    # Convert PIL image to bytes
                    jpg_buffer = BytesIO()
                    image.save(jpg_buffer, format="JPEG")
                    jpg_buffer.seek(0)

                    # --- DISPLAY AND DOWNLOAD ---
                    st.success("✅ Certificate Generated Successfully!")
                    
                    # Display the generated image
                    st.image(jpg_buffer, caption=f"Certificate for {new_name}")
                    
                    # Provide a download button for the JPG
                    st.download_button(
                        label="Download JPG 🖼️",
                        data=jpg_buffer,
                        file_name=f"Certificate_{new_name.replace(' ', '_')}.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error("❌ Could not convert PDF to JPG.")

        except FileNotFoundError:
            st.error(f"🚨 **Error:** The template file '{PDF_TEMPLATE_PATH}' was not found. Make sure it's in your GitHub repository.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("⚠️ Please enter a name to generate the certificate.")
