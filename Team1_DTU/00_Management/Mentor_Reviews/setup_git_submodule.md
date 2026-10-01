# Hướng Dẫn Thiết Lập Git Submodule (Project Management)

Tài liệu này tóm tắt quy trình thiết lập repository quản lý chính (`project-management`) tích hợp các repository thành phần (`backend`, `frontend`, `docs`, `tests`) thông qua cơ chế Git Submodule.

## 1. Cấu Trúc Dự Án Dự Kiến

```
project-management/
├── .gitmodules
├── backend/      # Submodule repo backend
├── frontend/     # Submodule repo frontend
├── docs/         # Submodule repo documentation
└── tests/        # Submodule repo e2e / integration tests

```

## 2. Các Bước Thiết Lập Ban Đầu

### Bước 1: Clone repo chính về máy

```
git clone git@github.com:<org-or-username>/project-management.git
cd project-management

```

### Bước 2: Thêm các repo con dưới dạng Submodule

Chạy lệnh `git submodule add` cho từng dịch vụ:

```
# Thêm backend
git submodule add git@github.com:<org-or-username>/project-backend.git backend

# Thêm frontend
git submodule add git@github.com:<org-or-username>/project-frontend.git frontend

# Thêm docs
git submodule add git@github.com:<org-or-username>/project-docs.git docs

# Thêm tests
git submodule add git@github.com:<org-or-username>/project-tests.git tests

```

*Lưu ý: Lệnh trên sẽ tự động tạo file `.gitmodules` tại thư mục gốc.*

### Bước 3: Cấu hình nhánh mặc định để theo dõi (Tùy chọn)

Mặc định Git submodule theo dõi commit cụ thể. Để tiện kéo update theo nhánh `main`:

```
git config -f .gitmodules submodule.backend.branch main
git config -f .gitmodules submodule.frontend.branch main
git config -f .gitmodules submodule.docs.branch main
git config -f .gitmodules submodule.tests.branch main

```

### Bước 4: Commit và Push lên repo chính

```
git add .gitmodules backend frontend docs tests
git commit -m "chore: initialize submodules (backend, frontend, docs, tests)"
git push origin main

```

## 3. Các Lệnh Thao Tác Thường Dùng (Cheatsheet)

| Tình huống | Lệnh thực hiện | 
 | ----- | ----- | 
| **Clone repo chính lần đầu (kèm toàn bộ submodules)** | `git clone --recurse-submodules <url-repo-management>` | 
| **Đã lỡ clone repo chính nhưng chưa tải submodules** | `git submodule update --init --recursive` | 
| **Kéo bản cập nhật mới nhất của tất cả submodules** | `git submodule update --remote --merge` | 
| **Kiểm tra trạng thái commit của các submodules** | `git submodule status` | 

## 4. Quy Trình Cập Nhật Commit Của Submodule Lên Repo Chính

Khi repo con (`backend`, `frontend`, ...) có commit mới cần liên kết vào repo chính:

```
# 1. Chuyển vào thư mục module con và cập nhật code mới
cd backend
git checkout main
git pull origin main

# 2. Quay lại thư mục gốc và commit con trỏ commit mới
cd ..
git add backend
git commit -m "feat(backend): bump submodule to latest commit"
git push origin main

```