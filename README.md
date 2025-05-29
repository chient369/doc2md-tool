# CTV Converter

## Giới thiệu
CTV Converter là một công cụ dòng lệnh mạnh mẽ giúp chuyển đổi các tài liệu (PDF, Excel, Word, PPTX, ...) thành file Markdown. Công cụ này tích hợp với Cursor AI để thực hiện truy vấn tìm kiếm thông tin dự án dưới nhiều loại files, giúp tối ưu hóa quy trình làm việc và quản lý tài liệu.

## Yêu cầu hệ thống
- Python >= 3.6
- Pip
- Git

## Hướng dẫn cài đặt
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

Sau khi cài đặt, mở lại terminal (hoặc chạy `source ~/.bashrc` trên Linux/MacOS) để sử dụng lệnh `cvmd` ở bất cứ đâu.

## Cấu hình
File `convert_config.json` cho phép cấu hình các định dạng file cần chuyển đổi. Ví dụ:
```json
{
    "file_types": [".pdf", ".xlsx", ".docx", ".pptx", ".xls"],
    "ignore_patterns": ["*.pdf", "*.xlsx", "*.docx", "*.pptx", "*.xls"]
}
```

## Hướng dẫn sử dụng
Chuyển đổi file trong thư mục hiện tại:
```cmd
cvmd
```
Chuyển đổi file trong thư mục khác và xuất ra thư mục tùy chọn:
```cmd
cvmd --input "C:\Documents" --output "C:\Markdown"
```

## Tham số dòng lệnh
- `--input, -i`: Thư mục chứa các file cần chuyển đổi (mặc định: thư mục hiện tại)
- `--output, -o`: Thư mục đầu ra cho file Markdown (mặc định: `doc_base`)
- `--config, -c`: Đường dẫn file cấu hình JSON (mặc định: `convert_config.json`)

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

## License
MIT License 