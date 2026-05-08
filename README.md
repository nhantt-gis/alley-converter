# Alley-converter

Chuyển đổi toàn bộ file CSV trong một thư mục sang **GeoPackage (GPKG)**.

- Quét tất cả `*.csv` trong thư mục `input/`
- Mỗi file thành một layer riêng (tên layer = tên file)
- Tổng hợp tất cả thành một layer `combined`
- Parse cột `geometry` (GeoJSON string, hỗ trợ cả `Feature` object)
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

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Sử dụng PowerShell

```bat
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu gặp lỗi `running scripts is disabled`, chạy tạm trong phiên hiện tại:

```bat
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Sử dụng

```bash
# Đọc tất cả CSV trong input/ -> output/data.gpkg
python main.py

# Chỉ định thư mục và file output
python main.py -i path/to/csv_folder -o path/to/output.gpkg

# Đổi tên layer tổng hợp
python main.py --combined-layer all_alleys

# Xem tất cả tùy chọn
python main.py --help
```

## Tùy chọn

| Flag                | Mặc định           | Mô tả                                    |
| ------------------- | ------------------ | ---------------------------------------- |
| `-i`, `--input`     | `input`            | Thư mục chứa các file CSV đầu vào        |
| `-o`, `--output`    | `output/data.gpkg` | File GPKG đầu ra                         |
| `--combined-layer`  | `combined`         | Tên layer tổng hợp tất cả features       |

## Cấu trúc

```
alley-converter/
├── main.py           # tool chính
├── requirements.txt  # dependencies
├── input/            # đặt các file CSV vào đây
│   ├── alleys_q1.csv
│   ├── alleys_q2.csv
│   └── ...
└── output/           # file GPKG được ghi ra đây
    └── data.gpkg     # chứa layer per-file + layer combined
```

## Yêu cầu dữ liệu đầu vào

Mỗi file CSV cần có cột `geometry` chứa GeoJSON hợp lệ.  
Tên layer trong GPKG được đặt theo tên file CSV (bỏ phần `.csv`).

Nếu tên cột thay đổi, chỉnh constant ở đầu `main.py`:

```python
INPUT_GEOMETRY_COLUMN = "geometry"
OUTPUT_CRS = "EPSG:4326"
```
