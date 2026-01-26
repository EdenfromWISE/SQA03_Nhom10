# Hướng dẫn đẩy code lên GitHub

## Bước 1: Khởi tạo Git Repository

```bash
# Di chuyển vào thư mục project
cd my-frontend

# Khởi tạo git repository
git init

# Thêm tất cả files vào staging area
git add .

# Commit lần đầu
git commit -m "Initial commit: Language Learning Platform Frontend"
```

## Bước 2: Tạo Repository trên GitHub

1. Truy cập [GitHub.com](https://github.com)
2. Đăng nhập vào tài khoản
3. Click "New repository" (nút + ở góc phải)
4. Điền thông tin:
   - **Repository name**: `language-learning-platform-frontend`
   - **Description**: `Frontend for Language Learning Platform built with React`
   - **Visibility**: Public hoặc Private (tùy chọn)
   - **Initialize**: Không tích vào các tùy chọn này vì đã có code

## Bước 3: Kết nối Local Repository với GitHub

```bash
# Thêm remote origin (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/language-learning-platform-frontend.git

# Kiểm tra remote đã được thêm
git remote -v
```

## Bước 4: Đẩy code lên GitHub

```bash
# Đẩy code lên branch main
git branch -M main
git push -u origin main
```

## Bước 5: Cấu hình GitHub Repository

### Thêm Topics/Tags
- Vào Settings > General > Topics
- Thêm các tags: `react`, `javascript`, `frontend`, `language-learning`, `education`

### Cấu hình Branch Protection (Optional)
- Vào Settings > Branches
- Add rule cho branch `main`
- Enable "Require pull request reviews before merging"

### Thêm GitHub Pages (Optional)
- Vào Settings > Pages
- Source: Deploy from a branch
- Branch: `main` / `root`

## Bước 6: Tạo GitHub Actions cho CI/CD (Optional)

Tạo file `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build
      run: npm run build
      
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./dist
```

## Lệnh Git hữu ích

```bash
# Xem trạng thái repository
git status

# Xem lịch sử commit
git log --oneline

# Thêm file cụ thể
git add filename.js

# Commit với message chi tiết
git commit -m "feat: add user authentication with Google OAuth"

# Push lên branch khác
git push origin feature-branch

# Pull latest changes
git pull origin main

# Tạo branch mới
git checkout -b feature/new-feature

# Chuyển về branch main
git checkout main
```

## Troubleshooting

### Lỗi: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/repository-name.git
```

### Lỗi: "failed to push some refs"
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

### Lỗi: "authentication failed"
- Kiểm tra username/password
- Hoặc sử dụng Personal Access Token thay vì password
- Cấu hình SSH key nếu cần

## Cấu hình SSH (Recommended)

```bash
# Tạo SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Thêm SSH key vào GitHub
# Copy nội dung file ~/.ssh/id_ed25519.pub
# Vào GitHub Settings > SSH and GPG keys > New SSH key

# Test SSH connection
ssh -T git@github.com

# Clone repository với SSH
git clone git@github.com:YOUR_USERNAME/repository-name.git
```
