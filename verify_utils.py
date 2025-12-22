
import io
import fitz
from fastapi import UploadFile
from utl.file_util import FileUtil
from PIL import Image

def test_pdf_validation():
    # Create a dummy PDF in memory
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World")
    pdf_bytes = doc.tobytes()
    doc.close()

    # Mock UploadFile
    file_obj = io.BytesIO(pdf_bytes)
    upload_file = UploadFile(file=file_obj, filename="test.pdf")

    is_valid = FileUtil.is_valid_pdf(upload_file)
    print(f"PDF Validation Result: {is_valid}")
    assert is_valid == True, "Should be a valid PDF"

    # Reset and test invalid
    file_obj = io.BytesIO(b"not a pdf")
    upload_file = UploadFile(file=file_obj, filename="fake.pdf")
    is_valid = FileUtil.is_valid_pdf(upload_file)
    print(f"Invalid PDF Validation Result: {is_valid}")
    assert is_valid == False, "Should be an invalid PDF"

def test_image_validation():
    # Create a dummy Image
    img = Image.new('RGB', (60, 30), color = 'red')
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format='JPEG')
    img_bytes = img_bytes_io.getvalue()

    # Mock UploadFile
    file_obj = io.BytesIO(img_bytes)
    upload_file = UploadFile(file=file_obj, filename="test.jpg")

    is_valid = FileUtil.is_valid_image(upload_file)
    print(f"Image Validation Result: {is_valid}")
    assert is_valid == True, "Should be a valid Image"

if __name__ == "__main__":
    try:
        test_pdf_validation()
        test_image_validation()
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
