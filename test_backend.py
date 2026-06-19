import requests
import time

def test_upload():
    # Create a dummy PDF file for testing
    with open("dummy.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 21 >>\nstream\nBT /F1 12 Tf 100 700 Td (Hello World) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000213 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n283\n%%EOF")

    url = "http://127.0.0.1:8000/api/upload"
    files = {"file": ("dummy.pdf", open("dummy.pdf", "rb"), "application/pdf")}
    
    print("Uploading file to backend...")
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        job_id = data.get("job_id")
        print(f"✅ Upload successful. Job ID: {job_id}")
        
        print("Polling status...")
        for _ in range(5):
            status_res = requests.get(f"http://127.0.0.1:8000/api/status/{job_id}")
            if status_res.status_code == 200:
                status_data = status_res.json()
                print(f"Status: {status_data['status']} | Progress: {status_data['progress']}")
                if status_data['status'] in ["COMPLETED", "FAILED"]:
                    break
            time.sleep(2)
            
        print("Fetching report...")
        report_res = requests.get(f"http://127.0.0.1:8000/api/report/{job_id}")
        if report_res.status_code == 200:
            print("✅ Report retrieved successfully!")
            print(report_res.json())
        else:
            print(f"❌ Failed to get report: {report_res.text}")
    else:
        print(f"❌ Upload failed: {response.text}")

if __name__ == "__main__":
    test_upload()
