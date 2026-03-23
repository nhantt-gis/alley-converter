# Alley-converter

Chuyển đổi dữ liệu từ Excel sang **GeoPackage (GPKG)**.

- Đọc cột `geometry` trong file Excel
- Parse GeoJSON string (hỗ trợ cả object `Feature` hoặc geometry object)
- Xuất ra file `.gpkg` tương thích QGIS / ArcGIS

---

## Clone repository

```bash
git clone https://github.com/nhantt-gis/alley-converter.git
cd alley-converter
```

## Cài đặt

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

#### Sử dụng Command Prompt

```bash
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Sử dụng PowerShell

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu gặp lỗi `running scripts is disabled`, chạy tạm trong phiên hiện tại:

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Sử dụng

### Linux / macOS

```bash
# Chạy với default (input/data.xlsx -> output/data.gpkg)
python main.py

# Truyền input/output tùy chỉnh
python main.py -i path/to/input.xlsx -o path/to/output.gpkg
```

### Windows

```bash
# Chạy với default (input\data.xlsx -> output\data.gpkg)
python main.py

# Truyền input/output tùy chỉnh
python main.py -i input\data.xlsx -o output\data.gpkg -l data
```

## Tùy chọn

| Flag             | Mặc định           | Mô tả                |
| ---------------- | ------------------ | -------------------- |
| `-i`, `--input`  | `input/data.xlsx`  | File Excel đầu vào   |
| `-o`, `--output` | `output/data.gpkg` | File GPKG đầu ra     |
| `-l`, `--layer`  | `data`             | Tên layer trong GPKG |

## Yêu cầu dữ liệu đầu vào

File Excel cần có cột `geometry` chứa GeoJSON hợp lệ.
