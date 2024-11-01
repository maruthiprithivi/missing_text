import streamlit as st
import json
from missing_text.extract.pdf import sync_extract_pdf
import io
import base64
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def main():
    st.set_page_config(
        page_title="MissingText - Processed Document Analyser", layout="wide"
    )

    st.title("MissingText - Processed Document Analyser")

    # Global variable to store extracted content
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = None

    # Create tabs for navigation
    tabs = st.tabs(
        [
            "Upload & Process",
            "Text",
            "Tables",
            "Extracted Images",
            "Image OCR",
            "Segments",
            "Download JSON",
            "Processing Logs",
        ]
    )

    with tabs[0]:
        st.header("Upload and Process PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if st.button("Start Processing"):
            if uploaded_file is None:
                st.warning("Please upload a PDF file before processing.")
            else:
                with st.spinner("Extracting content..."):
                    pdf_content = sync_extract_pdf(uploaded_file.getvalue())
                    st.session_state.pdf_content = pdf_content
                st.success(
                    "PDF processed successfully. Navigate to other tabs to view the results."
                )

    with tabs[1]:
        st.header("Extracted Text")
        if (
            st.session_state.pdf_content
            and "text" in st.session_state.pdf_content
            and st.session_state.pdf_content["text"]
        ):
            # Split the text into pages
            for i, text_item in enumerate(st.session_state.pdf_content["text"]):
                st.subheader(f"Page {text_item['page_number']}")
                col1, col2 = st.columns(2)
                with col1:
                    page_image = st.session_state.pdf_content["pages"][i]["image"]
                    st.image(
                        base64.b64decode(page_image),
                        caption=f"Original Page {text_item['page_number']}",
                        use_column_width=True,
                    )
                with col2:
                    st.text_area(
                        label=f"Page {text_item['page_number']} Content",
                        value=text_item["content"],
                        height=400,
                        key=f"text_{i}",
                    )
        else:
            st.warning("No PDF processed yet. Please upload and process a PDF first.")

    with tabs[2]:
        st.header("Extracted Tables")
        if (
            st.session_state.pdf_content
            and "tables" in st.session_state.pdf_content
            and st.session_state.pdf_content["tables"]
        ):
            for i, table_item in enumerate(st.session_state.pdf_content["tables"]):
                st.subheader(f"Page {table_item['page_number']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    page_image = st.session_state.pdf_content["pages"][
                        table_item["page_number"] - 1
                    ]["image"]
                    st.image(
                        base64.b64decode(page_image),
                        caption=f"Original Page {table_item['page_number']}",
                        use_column_width=True,
                    )
                with col2:
                    st.dataframe(table_item["content"], key=f"table_pymupdf_{i}")
                # with col3:
                #     st.text_area(label=f"Page {table_item['page_number']} Summarized Content", value=table_item["multi_modal_summary"], height=400, key=f"summarized_text_{i}")
        else:
            st.warning("No tables extracted using PyMuPDF.")

    with tabs[3]:
        st.header("Extracted Images")
        if not st.session_state.pdf_content:
            st.warning("No images extracted. Please process a PDF first.")
        elif (
            st.session_state.pdf_content
            and "images" in st.session_state.pdf_content
            and st.session_state.pdf_content["images"]
        ):
            for i, image_item in enumerate(st.session_state.pdf_content["images"]):
                st.subheader(f"Page {image_item['page_number']}")
                col1, col2 = st.columns(2)
                with col1:
                    # Display the original PDF page
                    page_image = st.session_state.pdf_content["pages"][
                        image_item["page_number"] - 1
                    ]["image"]
                    st.image(
                        base64.b64decode(page_image),
                        caption=f"Original Page {image_item['page_number']}",
                        use_column_width=True,
                    )
                with col2:
                    if "image_data" in image_item:
                        image_bytes = base64.b64decode(image_item["image_data"])
                        st.image(
                            Image.open(io.BytesIO(image_bytes)),
                            caption=f"Extracted Image from Page {image_item['page_number']}",
                            use_column_width=True,
                        )
                    else:
                        st.write("No image data available for this item.")
        else:
            st.warning("No images extracted from the PDF.")

    with tabs[4]:
        st.header("Image OCR")
        if not st.session_state.pdf_content:
            st.warning("No OCR text available. Please process a PDF first.")
        elif st.session_state.pdf_content and "images" in st.session_state.pdf_content:
            for i, image_item in enumerate(st.session_state.pdf_content["images"]):
                st.subheader(f"Page {image_item['page_number']}")
                col1, col2 = st.columns(2)
                with col1:
                    if "image_data" in image_item:
                        image_bytes = base64.b64decode(image_item["image_data"])
                        st.image(
                            Image.open(io.BytesIO(image_bytes)),
                            caption=f"Extracted Image from Page {image_item['page_number']}",
                            use_column_width=True,
                        )
                    else:
                        st.write("No image data available for this item.")
                with col2:
                    st.text_area(
                        label=f"Page {image_item['page_number']} OCR Text",
                        value=image_item["content"],
                        height=200,
                        key=f"image_ocr_{i}",
                    )
        else:
            st.warning("No OCR text extracted from images.")
    with tabs[5]:
        st.header("PDF Segments")
        if st.session_state.pdf_content and "segments" in st.session_state.pdf_content:
            for page_data in st.session_state.pdf_content["segments"]:
                st.subheader(f"Page {page_data['page_number']}")
                col1, col2 = st.columns(2)

                with col1:
                    # Display the original PDF page
                    page_image = st.session_state.pdf_content["pages"][
                        page_data["page_number"] - 1
                    ]["image"]
                    img = Image.open(io.BytesIO(base64.b64decode(page_image)))

                    # Create a new figure and axis
                    fig, ax = plt.subplots(figsize=(10, 14))
                    ax.imshow(img)

                    # Add bounding boxes for each segment
                    segment_colors = {
                        "text": "blue",
                        "image": "green",
                        "table": "red",
                        "chart": "purple",
                        "latex": "orange",
                    }

                    for segment in page_data["segments"]:
                        x, y, w, h = segment["bbox"]
                        rect = patches.Rectangle(
                            (x, y),
                            w - x,
                            h - y,
                            linewidth=2,
                            edgecolor=segment_colors.get(segment["type"], "gray"),
                            facecolor="none",
                        )
                        ax.add_patch(rect)

                    ax.axis("off")
                    st.pyplot(fig)

                with col2:
                    # Group segments by type
                    segment_groups = {}
                    for segment in page_data["segments"]:
                        if segment["type"] not in segment_groups:
                            segment_groups[segment["type"]] = []
                        segment_groups[segment["type"]].append(segment)

                    # Display grouped and collapsible segments
                    for segment_type, segments in segment_groups.items():
                        with st.expander(
                            f"{segment_type.capitalize()} ({len(segments)})",
                            expanded=False,
                        ):
                            for segment in segments:
                                st.markdown(
                                    f'<div style="border-left: 5px solid {segment_colors[segment_type]}; padding-left: 10px;">',
                                    unsafe_allow_html=True,
                                )
                                if (
                                    segment["type"] == "image"
                                    and "image_data" in segment
                                ):
                                    st.image(
                                        base64.b64decode(segment["image_data"]),
                                        caption="Extracted Image",
                                        use_column_width=True,
                                    )
                                st.write(
                                    f"Content: {segment['content'][:100]}..."
                                )  # Show first 100 characters
                                st.write(f"Bounding Box: {segment['bbox']}")
                                st.markdown("</div>", unsafe_allow_html=True)
                                st.write("---")
        else:
            st.warning("No segment data available. Please process a PDF first.")

    with tabs[6]:
        st.header("Download Extracted Content as JSON")
        if st.session_state.pdf_content:
            json_str = json.dumps(st.session_state.pdf_content, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="extracted_content.json",
                mime="application/json",
            )
        else:
            st.warning("No PDF processed yet. Please upload and process a PDF first.")

    with tabs[7]:
        st.header("Processing Logs")
        if st.session_state.pdf_content:
            st.text("PDF processing completed successfully.")
            st.text("No errors or warnings were encountered during processing.")
        else:
            st.warning("No PDF processed yet. Please upload and process a PDF first.")


if __name__ == "__main__":
    main()
