import json
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline

# 1. Tải và chuẩn bị dữ liệu
base_dir = Path(__file__).resolve().parent
data_file = base_dir / "data.json"

with open(data_file, "r", encoding="utf-8") as f:
    data = json.load(f)["nlu_data"]

texts = [item["text"] for item in data]
intents = [item["intent"] for item in data]

# 2. Xây dựng pipeline xử lý và huấn luyện
# Pipeline này sẽ tự động:
# a. Chuyển văn bản thành vector số (TF-IDF)
# b. Huấn luyện mô hình phân loại (SVC - Support Vector Classifier)
model_pipeline = make_pipeline(TfidfVectorizer(), SVC(kernel="linear", probability=True))

print("Bắt đầu huấn luyện mô hình Intent...")
model_pipeline.fit(texts, intents)
print("Huấn luyện hoàn tất!")

# 3. Lưu mô hình đã huấn luyện ra file
# Chúng ta lưu cả pipeline để có thể tái sử dụng chính xác TfidfVectorizer
model_file = base_dir / "intent_model.joblib"
joblib.dump(model_pipeline, model_file)
print(f"Đã lưu mô hình Intent vào file {model_file}")

# Cách sử dụng thử:
test_sentence = "từ computer nghĩa là gì"
predicted_intent = model_pipeline.predict([test_sentence])[0]
print(f"Câu '{test_sentence}' -> Intent dự đoán: {predicted_intent}")

