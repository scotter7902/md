# Hướng dẫn sử dụng Malware Detection
Malware Detection là chương trình hỗ trợ phát hiện malware và các file PE độc hại dựa trên học sâu.

*Yêu cầu:*
- Python 3.
- Phiên bản mới nhất của pip.
- Chạy file auto_setup.bat để cài đặt các package cần thiết.
## Training
### 1. data.py: Tách feature
Chức năng: Tách các feature từ các file PE trong một thư mục xác định vào 1 file csv.
- **create_data**(raw data path[, data type=2[, output csv file path=None]]);

-- **raw data path**: Đường dẫn đến thư mục chứa các file PE.

-- **data type**: Dán nhãn cho các file PE đó: 0: malware, 1: normal file, 2: unknow (mặc định là 2).

-- **output csv file path**: Đường dẫn chứa file csv sau khi tách lấy features từ các file PE (1 file csv chứa toàn bộ feature từ các file PE) (đường dẫn mặc định là None).

*Lưu ý:*

-- *Mỗi thư mục chỉ nên chứ một loại PE (malware, normal file).*

-- Nếu đường dẫn tồn tại file csv thì sẽ append thêm vào file csv đó.
### 2. cnn.py: Training model
Chức năng: Training model từ các file csv đã tách ra thông tin feature.
- **cnn**(csv file path, training epochs[, old model=None]);

-- **csv file path**: Đường dẫn chứa file csv đã tách ra từ malware (file csv chỉ chứa malware) hoặc dataframe chứa thông tin features của các file malware PE.

-- **training epochs**: Số lần lặp lại tập data trong quá trình training.

-- **old model**: Đường dẫn chứa file model (.h5) mà bạn muốn cập nhật thêm vào, nếu để trống thì chương trình sẽ tạo một file model mới ở đường dẫn ***trained/model.h5***.
- Các thông số mặc định:

-- Đường dẫn chứa file csv của legit PE: ***dataset/legit.csv***.

-- Batch size: ***512***.

-- Tỉ lệ malware/benign: ***70/30***.

*Lưu ý: Phải đưa file csv của legit PE vào đúng đường dẫn trained/model.h5.*
## Sử dụng
### 1. scan.py: Scan file và folder
Chức năng: quét các file malware PE bằng phương pháp học sâu từ những dữ liệu đã học được.

*Yêu cầu: File model phải nằm ở đường dẫn: ***trained/model.h5***.*
- **scan.py** **argument**

-- argument: 0: scan folder, 1: scan file.
