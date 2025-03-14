
# API Endpoints

### 1. Test Database
- **Method:** `GET`
- **Path:** `/tests-db`
- **Mô tả:** Kiểm tra kết nối database.
- **Request:** Không có tham số.
- **Response:**
  ```json
  {
    "message": "Database connection successful"
  }
  ```

### 2. Infer Category
- **Method:** `POST`
- **Path:** `/api/v1/category/infer`
- **Mô tả:** Dự đoán danh mục từ từ khóa.
- **Request:**
  ```json
  {
    "keywords": ["phone", "good"]
  }
  ```
- **Response:**
  ```json
  {
    "session_id": "abc123",
    "messages": [
      {
        "message_id": "msg1",
        "timestamp": "2025-03-12T07:51:50.236021+00:00Z",
        "sender": "chatbot",
        "text": "Danh mục suy luận: Công nghệ",
        "attachments": []
      }
    ],
    "context": {
      "conversation_state": "active",
      "intent": "category_inference",
      "entities": {
        "keywords": ["phone", "good"],
        "category": "Công nghệ",
        "date": "2025-03-12T07:51:50.236021+00:00Z"
      }
    }
  }
  ```
- **Lỗi:** 
  - Status `400`:
    ```json
    {
      "detail": "Keywords cannot be empty"
    }
    ```

### 3. Analyze Text
- **Method:** `POST`
- **Path:** `/api/v1/analyzer/analyze`
- **Mô tả:** Phân tích hoặc làm rõ truy vấn.
- **Request:**
  ```json
  {
    "query": "Có điện thoại nào tốt không?",
    "session_id": "xyz789"
  }
  ```
- **Response:**
  - Truy vấn mơ hồ:
    ```json
    {
      "session_id": "xyz789",
      "messages": [
        {
          "message_id": "msg2",
          "timestamp": "2025-03-12T07:51:50.236021+00:00Z",
          "sender": "chatbot",
          "text": "Bạn có thể nói rõ hơn không? Ví dụ như bạn muốn tìm điện thoại tốt về mặt nào?",
          "attachments": []
        }
      ],
      "context": {
        "conversation_state": "clarification_needed",
        "intent": "ambiguous_query",
        "entities": {
          "original_query": "Có điện thoại nào tốt không?",
          "date": "2025-03-12T07:51:50.236021+00:00Z"
        }
      }
    }
    ```
- **Lỗi:** 
  - Status `500`:
    ```json
    {
      "detail": "Không thể phân loại query"
    }
    ```

### 4. Chat
- **Method:** `POST`
- **Path:** `/api/v1/chatbot/chat`
- **Mô tả:** Gửi truy vấn để trò chuyện với chatbot.
- **Request:**
  ```json
  {
    "query": "Xin chào",
    "session_id": "def456"
  }
  ```
- **Response:**
  ```json
  {
    "session_id": "def456",
    "messages": [
      {
        "message_id": "msg3",
        "timestamp": "2025-03-12T07:51:50.236021+00:00Z",
        "sender": "chatbot",
        "text": "Chào bạn! Tôi có thể giúp gì?",
        "attachments": []
      }
    ],
    "context": {
      "conversation_state": "active",
      "intent": "conversation",
      "entities": {
        "input_query": "Xin chào",
        "date": "2025-03-12T07:51:50.236021+00:00Z"
      }
    }
  }
  ```

### 5. Get Chat History
- **Method:** `POST`
- **Path:** `/api/v1/chatbot/history`
- **Mô tả:** Lấy lịch sử trò chuyện theo session.
- **Request:**
  ```json
  {
    "session_id": "def456",
    "limit": 1
  }
  ```
- **Response:**
  ```json
  {
    "session_id": "def456",
    "messages": [
      {
        "message_id": "msg3",
        "timestamp": "2025-03-12T07:51:50.236021+00:00Z",
        "sender": "chatbot",
        "text": "Chào bạn! Tôi có thể giúp gì?",
        "attachments": []
      }
    ],
    "context": {
      "conversation_state": "active",
      "intent": "retrieve_history",
      "entities": {
        "total_messages": 2,
        "retrieved_count": 1,
        "date": "2025-03-12T07:51:50.236021+00:00Z"
      }
    }
  }
  ```

## Chú thích
- **Session ID:** Lưu `session_id` từ phản hồi để dùng lại.
- **Lỗi:** Kiểm tra mã trạng thái HTTP và hiển thị `detail`.
- **chatbotAPI:** Lấy schema tại `/chatbotAPI.json` để test trong Postman/Swagger.
