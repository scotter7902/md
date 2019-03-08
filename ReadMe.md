# Malware Detection Deep Learning
## 1. Lọc file thực thi từ một đống file mà bạn đéo bik nó ở đâu
Bình tĩnh, thả cái đống bùi nhùi đó vào thư mục ***legit_exec_file_filter/raw_data*** và chạy ngay ***LegitExecFileFilter.py***. Toàn bộ file thực thi sẽ được lọc ra và chuyển qua thư mục ***data/legitimate***.
## 2. Trích xuất thuộc tính file thực thi
Chỉ cần chạy ***ExtractData.py*** và toàn bộ thuộc tính của file thực thi trong thư mục ***data*** sẽ được import vào file ***data/data.csv***.