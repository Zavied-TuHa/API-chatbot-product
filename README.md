# API Chatbot-Product

API chatbot-product bao gồm các API sử dụng để xử lý truy vấn người dùng, phân tích văn bản, suy luận danh mục, và duy trì lịch sử trò chuyện.
Dự án sử dụng FastAPI để phát triển API và tích hợp trí tuệ nhân tạo qua LangChain với mô hình ngôn ngữ lớn (LLM) Gemini từ Google.

## Mục tiêu đề ra
- Cung cấp API cho phép người dùng tương tác với chatbot qua các endpoint như `/chatbot/chat` và `/chatbot/history`.
- Phân tích truy vấn người dùng (`/analyzer/analyze`) và làm rõ khi cần.
- Dự đoán danh mục từ từ khóa (`/category/infer`) để hỗ trợ phân loại sản phẩm/dịch vụ.
- Đảm bảo tính ổn định qua kiểm thử tự động với Pytest và tài liệu hóa API cho frontend.

## 1. Công nghệ sử dụng
- **Backend:** Python 3.13, FastAPI, Uvicorn
- **AI Integration:** LangChain 0.3.19 (core, community), Google GenerativeAI (Gemini LLM)
- **Tracing:** LangSmith
- **HTTP Client:** HTTPX (test), Requests (manual test)
- **Data Validation:** Pydantic, Pydantic-Settings
- **Environment:** Python-dotenv
- **Testing:** Pytest
- **Version Control:** Git, GitLab
- **Tools:** Postman Desktop, Pycharm Community

## 2. Chức năng các API
1. **Chatbot Interaction:** Gửi truy vấn và nhận phản hồi qua `/chatbot/chat`.
2. **History Retrieval:** Xem lịch sử trò chuyện với `/chatbot/history`.
3. **Text Analysis:** Phân tích hoặc làm rõ truy vấn qua `/analyzer/analyze`.
4. **Category Inference:** Dự đoán danh mục từ từ khóa với `/category/infer`.

## 3. Cài đặt

### Yêu cầu
- Python 3.12+
- Git
- API Keys:
  - Google API Key (cho Gemini)
  - LangChain API Key (cho LangSmith tracing, tùy chọn)

1. **Clone repository**:
   ```bash
   git clone https://github.com/Zavied-TuHa/API-chatbot-product.git
   cd API-chatbot-product
   ```

2. **Tạo môi trường ảo**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Cài đặt dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình biến môi trường**:
   - Tạo file `.env` trong thư mục gốc
   - Copy nội dung tại `example.env` vào và sửa đổi

5. **Chạy ứng dụng locally:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - Truy cập `http://localhost:8000/docs` để xem tài liệu

## Hướng dẫn sử dụng
- **API Documentation:** Xem chi tiết endpoint trong `API_DOCUMENTATION.md`.
- **Test API:** Dùng Postman với các endpoint như:
  - `POST http://localhost:8000/api/v1/chatbot/chat`
    ```json
    {"query": "Xin chào", "session_id": "test123"}
    ```
- **Kiểm thử:** Chạy test suite:
  ```bash
  pytest tests/ -v
  ```
  
## Liên hệ
- **Email:** <workhaatu@gmail.com>