# GTEL Maps Alley Geodata Convert Tool

GTEL Maps Alley Geodata Convert Tool là CLI tool dùng để chuyển đổi nhiều file CSV 
có cột geometry dạng GeoJSON thành một file **GeoPackage (GPKG)**.

Tool được thiết kế cho dữ liệu hẻm/ngõ hoặc các lớp tuyến/điểm polygon nhỏ cần gom
theo từng layer để mở trực tiếp trên QGIS, ArcGIS hoặc các pipeline GIS khác.

## Tính năng chính

- Quét toàn bộ `*.csv` trong thư mục đầu vào.
- Mỗi CSV được ghi thành một layer riêng trong cùng file `.gpkg`.
- Tự tạo layer tổng hợp, mặc định là `combined`.
- Parse cột geometry dạng GeoJSON `Geometry` hoặc `Feature`.
- Hỗ trợ đổi tên cột geometry, CRS đầu ra và layer tổng hợp.
- CLI dùng `typer`, giao diện terminal dùng `rich`.
- Quản lý dependency bằng `uv`.
- Có `Taskfile`, `Dockerfile`, `docker-compose.yml` và test cơ bản.

## Cài đặt nhanh

Yêu cầu:

- Python `>=3.11`
- `uv`
- Taskfile CLI nếu muốn dùng lệnh `task`
- Docker nếu muốn chạy bằng container

```bash
uv sync
```

Kiểm tra CLI:

```bash
uv run alley-converter --help
```

## Cách sử dụng

Đặt các file CSV vào thư mục `data/`, sau đó chạy:

```bash
uv run alley-converter
```

Kết quả mặc định:

```text
data/data.gpkg
```

Ví dụ tùy chỉnh:

```bash
uv run alley-converter \
  --input data \
  --output data/alleys.gpkg \
  --combined-layer all_alleys \
  --geometry-column geometry \
  --crs EPSG:4326
```

Giữ tương thích với entrypoint cũ:

```bash
uv run python main.py -i data -o data/data.gpkg
```

## Taskfile

Các lệnh thường dùng:

```bash
task sync
task run -- -i data -o data/data.gpkg
task test
task lint
task format
task docker-build
task docker-run
```

`task run -- ...` truyền toàn bộ tham số phía sau `--` vào CLI `alley-converter`.

## Docker

Build image:

```bash
docker compose build
```

Chạy với mount mặc định:

```bash
docker compose run --rm alley-converter
```

Compose mặc định mount:

- `./data` -> `/app/data` để đọc CSV và ghi file `.gpkg`

Truyền tham số riêng:

```bash
docker compose run --rm alley-converter \
  --input /app/data \
  --output /app/data/alleys.gpkg \
  --combined-layer all_alleys
```

## Định dạng dữ liệu đầu vào

Mỗi CSV cần có một cột geometry, mặc định là `geometry`.

Ví dụ:

```csv
id,name,geometry
1,Alley 1,"{""type"": ""Point"", ""coordinates"": [106.7, 10.8]}"
2,Alley 2,"{""type"": ""LineString"", ""coordinates"": [[106.7, 10.8], [106.71, 10.81]]}"
```

Cột geometry hỗ trợ:

- GeoJSON Geometry: `Point`, `LineString`, `Polygon`, `MultiPolygon`, ...
- GeoJSON Feature có trường `geometry`.

Nếu geometry không parse được, mặc định dòng dữ liệu vẫn được giữ với geometry null.
Muốn loại bỏ các dòng này:

```bash
uv run alley-converter --drop-invalid-geometry
```

## CLI reference

| Tùy chọn | Mặc định | Mô tả |
| --- | --- | --- |
| `-i`, `--input` | `data` | Thư mục chứa CSV đầu vào |
| `-o`, `--output` | `data/data.gpkg` | File GeoPackage đầu ra |
| `--combined-layer` | `combined` | Tên layer tổng hợp |
| `--geometry-column` | `geometry` | Tên cột chứa GeoJSON |
| `--crs` | `EPSG:4326` | CRS gán cho layer đầu ra |
| `--overwrite / --no-overwrite` | `--overwrite` | Ghi đè file output đã tồn tại |
| `--drop-invalid-geometry / --keep-invalid-geometry` | `--keep-invalid-geometry` | Loại hoặc giữ dòng có geometry lỗi |
| `--version` | | In phiên bản CLI |

## Cấu trúc dự án

```text
gtelmaps-alley-geodata-convert-tool/
├── src/
│   └── alley_converter/
│       ├── __init__.py        # package metadata
│       ├── __main__.py        # python -m alley_converter
│       ├── cli.py             # Typer CLI và Rich output
│       ├── config.py          # default config và ConverterConfig
│       ├── converter.py       # pipeline CSV -> GeoDataFrame -> GeoPackage
│       ├── exceptions.py      # exception domain-level
│       └── geometry.py        # parse GeoJSON -> Shapely geometry
├── tests/                 # unit/integration tests
├── data/                  # CSV đầu vào và GPKG đầu ra mặc định
├── main.py                # entrypoint tương thích với phiên bản cũ
├── pyproject.toml         # cấu hình uv, dependencies, ruff, pytest
├── uv.lock                # lockfile dependency
├── Taskfile.yml           # lệnh dev thường dùng
├── Dockerfile             # container runtime
├── docker-compose.yml     # chạy converter với volume data
└── requirements.txt       # legacy dependency list
```

## Kiến trúc xử lý

1. `cli.py` nhận tham số từ người dùng và tạo `ConverterConfig`.
2. `converter.py` tìm CSV, đọc bằng pandas, chuyển sang GeoDataFrame bằng GeoPandas.
3. `geometry.py` parse GeoJSON string thành Shapely geometry.
4. Mỗi GeoDataFrame được ghi thành một layer trong GeoPackage.
5. Các GeoDataFrame hợp lệ được concat thành layer tổng hợp.
6. CLI hiển thị bảng kết quả, số feature, số geometry lỗi và file bị skip.

## Phát triển

Cài dependency:

```bash
uv sync
```

Chạy test:

```bash
uv run pytest
```

Lint:

```bash
uv run ruff check .
```

Format:

```bash
uv run ruff format .
```

## Roadmap

### Đã triển khai

- [x] Chuyển đổi nhiều CSV thành các layer trong một GeoPackage.
- [x] Tạo layer tổng hợp `combined`.
- [x] Parse GeoJSON Geometry và Feature bằng Shapely.
- [x] CLI dùng Typer và Rich.
- [x] Quản lý dependency bằng uv.
- [x] Tổ chức source theo `src/alley_converter`.
- [x] Thêm Taskfile, Dockerfile và docker-compose.
- [x] Thêm test cơ bản cho parser và converter.

### Ưu tiên tiếp theo

- [ ] Thêm schema validation bắt buộc cho các trường nghiệp vụ.
- [ ] Thêm tùy chọn reprojection khi dữ liệu đầu vào có CRS khác.
- [ ] Xuất báo cáo chuyển đổi dạng JSON/CSV cho CI hoặc batch jobs.
- [ ] Thêm logging file và mã lỗi chuẩn hóa cho pipeline production.

### Ý tưởng tương lai

- [ ] Hỗ trợ đọc GeoJSON/Shapefile/Excel ngoài CSV.
- [ ] Thêm benchmark cho dữ liệu lớn và chunked processing.
- [ ] Đóng gói release qua GitHub Actions.
