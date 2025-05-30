# CTV Converter

## Giới thiệu
CTV Converter là một công cụ dòng lệnh mạnh mẽ giúp chuyển đổi các tài liệu (PDF, Excel, Word, PPTX, ...) thành file Markdown. Công cụ này tích hợp với Cursor AI để thực hiện truy vấn tìm kiếm thông tin dự án dưới nhiều loại files, giúp tối ưu hóa quy trình làm việc và quản lý tài liệu.

## Yêu cầu hệ thống
- Python >= 3.6 (khuyến nghị Python 3.10+)
- Pip
- Git

## Hướng dẫn cài đặt

Sau khi clone package về local thực hiện  1 trong 2 cách dưới.

### Cách 1: Cài đặt thủ công (mọi hệ điều hành)
```cmd
pip install .
```

### Cách 2: Tự động bằng script
#### Windows (PowerShell)
```powershell
cd scripts
powershell ./setup_convert.ps1
```
- Tham số `-RepoDir` (tùy chọn): Thư mục clone về, mặc định là `C:\doc2md-tool`

#### Linux/MacOS (Shell)
```bash
cd scripts
chmod +x setup_convert.sh
./setup_convert.sh [<thu_muc_clone>]
```
- Nếu không truyền `<thu_muc_clone>`, mặc định là `~/doc2md-tool`

### Cách 3: Cài đặt MarkItDown với đầy đủ tính năng
```powershell
cd scripts
powershell ./setup_markitdown.ps1
```
- Tham số `-FromSource`: Nếu muốn cài từ mã nguồn GitHub
- Tham số `-VenvPath`: Đường dẫn tới thư mục môi trường ảo, mặc định là `.venv`
- Tham số `-Extras`: Các tính năng cần cài, mặc định là `all`

Sau khi cài đặt, mở lại terminal (hoặc chạy `source ~/.bashrc` trên Linux/MacOS) để sử dụng lệnh `cvmd` ở bất cứ đâu.

## Cấu hình
File `convert_config.json` cho phép cấu hình các định dạng file cần chuyển đổi và các tùy chọn khác. Ví dụ:
```json
{
    "file_types": [".pdf", ".xlsx", ".docx", ".pptx", ".xls", ".doc", ".xlsm", ".png", ".jpg", ".jpeg"],
    "ignore_patterns": ["node_modules", "venv", ".venv", "__pycache__", ".git"],
    "converter_options": {
        "pdf_ocr": true,
        "excel_table_format": "markdown",
        "pptx_extract_notes": true,
        "pptx_extract_images": false,
        "output_encoding": "utf-8"
    }
}
```

### Tùy chọn cấu hình

#### file_types
Danh sách các định dạng file cần chuyển đổi.

#### ignore_patterns
Danh sách các thư mục hoặc mẫu file cần bỏ qua khi chuyển đổi và thêm vào `.cursorignore`.

#### converter_options
Các tùy chọn cho công cụ chuyển đổi MarkItDown:
- `pdf_ocr`: Bật/tắt OCR cho file PDF (mặc định: true)
- `excel_table_format`: Định dạng bảng Excel (markdown, html, csv)
- `pptx_extract_notes`: Trích xuất ghi chú từ file PPTX (mặc định: true)
- `pptx_extract_images`: Trích xuất hình ảnh từ file PPTX (mặc định: false)
- `output_encoding`: Mã hóa đầu ra (mặc định: utf-8)

## Hướng dẫn sử dụng
### Chuyển đổi file
Chuyển đổi file trong thư mục hiện tại:
```cmd
cvmd
```
Chuyển đổi file trong thư mục khác và xuất ra thư mục tùy chọn:
```cmd
cvmd --input "C:\Documents" --output "C:\Markdown"
```

### Chỉ cài đặt MarkItDown
Nếu bạn muốn chỉ cài đặt MarkItDown và các phụ thuộc mà không chuyển đổi file:
```cmd
cvmd --setup-only
```

## Tham số dòng lệnh
- `--input, -i`: Thư mục chứa các file cần chuyển đổi (mặc định: thư mục hiện tại)
- `--output, -o`: Thư mục đầu ra cho file Markdown (mặc định: `doc_base`)
- `--config, -c`: Đường dẫn file cấu hình JSON (mặc định: `convert_config.json`)
- `--setup-only`: Chỉ cài đặt MarkItDown và các phụ thuộc mà không chuyển đổi file

## Ví dụ sử dụng
```cmd
cvmd -i ./documents -o ./md_output -c custom_config.json
```

## Quản lý mã nguồn với Git
Dự án đã có sẵn file `.gitignore` để loại trừ các file/thư mục không cần thiết khỏi source control, bao gồm:
- Thư mục output chuyển đổi (`/doc_base/`)
- File cấu hình cá nhân (`convert_config.json`)
- File metadata tự động sinh (`metadata.md`)
- File/thư mục môi trường ảo Python, cache, VSCode, Cursor...

## Thực hiện thêm cursor rules vào Cursor
Cursor Rules là tập hợp các quy tắc giúp Cursor AI hiểu cách tìm kiếm và truy xuất thông tin từ các tài liệu đã chuyển đổi. Để thêm nội dung này vào Cursor:

1. **Mở Cursor AI**: Khởi động ứng dụng Cursor AI trên máy tính của bạn.

2. **Truy cập Rules**: Mở phần Rules trong Cursor (thường nằm ở góc dưới bên trái hoặc trong menu Settings).

3. **Tạo Rule mới**:
   - Nhấp vào "Add New Rule" hoặc tùy chọn tương tự.
   - Đặt tên cho rule, ví dụ: "Document Search Standard".
   - Copy toàn bộ nội dung từ file `cursor_rules/docs-search-standard.md` và dán vào phần nội dung của rule.

4. **Lưu và kích hoạt Rule**:
   - Nhấp vào "Save" hoặc "Apply" để lưu rule.
   - Đảm bảo rule đã được kích hoạt (thường có một công tắc bật/tắt bên cạnh rule).

5. **Sử dụng Rule**:
   - Khi truy vấn trong Cursor, bạn có thể yêu cầu Cursor sử dụng rule này bằng cách đề cập đến tên của nó.
   - Ví dụ: "Sử dụng Document Search Standard để tìm thông tin về [chủ đề] trong tài liệu của tôi."

## Lưu ý
- Công cụ này chỉ hoạt động tốt trên Cursor AI và đã được tối ưu hóa cho môi trường này.
- Để đạt hiệu quả cao nhất, hãy sử dụng với Cursor AI phiên bản mới nhất.

## License
MIT License 