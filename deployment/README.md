# Redis Summary Auto-Summary Deployment

Hệ thống tự động tóm tắt dữ liệu Redis conversations với khả năng kết nối đến Redis server external.

## 🏗️ Kiến trúc

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Redis Server  │    │  Summary App     │    │   OpenAI API    │
│ 192.168.88.165  │◄───┤  (Docker)        │◄───┤                 │
│     :6379       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Yêu cầu

- Docker & Docker Compose
- Kết nối đến Redis server: `192.168.88.165:6379`
- OpenAI API Key

## 🚀 Cài đặt nhanh

### 1. Setup môi trường

```bash
cd deployment
./deploy.sh setup
```

### 2. Cấu hình API keys

Chỉnh sửa file `.env`:
```bash
nano .env
```

Cập nhật:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Build ứng dụng

```bash
./deploy.sh build
```

## 🎯 Các chế độ chạy

### Manual Mode - Chạy summary thủ công
```bash
# Chạy một lần
./deploy.sh summary

# Hoặc start container để chạy thủ công nhiều lần
./deploy.sh start manual
```

### Scheduler Mode - Tự động chạy theo lịch
```bash
# Chạy scheduler tự động (mặc định: mỗi 1 giờ)
./deploy.sh start scheduler
```

### Tools Mode - Redis Commander
```bash
# Chạy Redis Commander để quản lý Redis
./deploy.sh start tools
# Truy cập: http://localhost:8081
```

## ⚙️ Cấu hình

### Biến môi trường (.env)

```env
# Redis Configuration (External Server)
REDIS_HOST=192.168.88.165
REDIS_PORT=6379

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
SCHEDULE_INTERVAL=3600    # Scheduler interval (seconds)
NUMBER_OF_SUMMARY=10      # Trigger summary after N new sessions
```

### Tùy chỉnh ngưỡng summary

Thay đổi `NUMBER_OF_SUMMARY` trong `.env` để điều chỉnh khi nào auto-summary được kích hoạt:
- `5`: Summary sau mỗi 5 session mới
- `10`: Summary sau mỗi 10 session mới (mặc định)
- `20`: Summary sau mỗi 20 session mới

## 📊 Giám sát

### Xem logs
```bash
# Tất cả logs
./deploy.sh logs

# Logs của scheduler
./deploy.sh logs scheduler

# Logs của app
./deploy.sh logs redis_summary_app
```

### Kiểm tra trạng thái
```bash
./deploy.sh status
```

## 🔧 Quản lý

### Khởi động lại services
```bash
./deploy.sh restart scheduler
```

### Dừng services
```bash
./deploy.sh stop
```

### Backup dữ liệu
```bash
./deploy.sh backup
```

### Dọn dẹp
```bash
./deploy.sh cleanup
```

## 🧪 Testing

### Chạy tests
```bash
./deploy.sh test
```

### Chạy demo
```bash
./deploy.sh demo
```

## 📁 Cấu trúc thư mục

```
deployment/
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Application container
├── requirements.txt     # Python dependencies
├── scheduler.py         # Scheduler service
├── deploy.sh           # Deployment script
├── .env.example        # Environment template
├── .env                # Your environment (create from .env.example)
├── logs/               # Application logs
├── data/               # Application data
└── backups/            # Backup files
```

## 🔍 Troubleshooting

### Lỗi kết nối Redis
```bash
# Kiểm tra kết nối đến Redis server
docker run --rm redis:7-alpine redis-cli -h 192.168.88.165 -p 6379 ping
```

### Lỗi OpenAI API
- Kiểm tra API key trong file `.env`
- Kiểm tra quota và billing của OpenAI account

### Container không start
```bash
# Xem logs chi tiết
./deploy.sh logs

# Rebuild container
./deploy.sh build
```

## 📈 Monitoring Production

### Scheduler logs
```bash
# Theo dõi scheduler real-time
docker-compose logs -f scheduler
```

### Summary results
Summary được lưu trong Redis với key pattern: `summary:memory:session_id`

### Metadata tracking
Metadata về lần summary cuối được lưu trong key: `summary_metadata`

## 🔄 Workflow tự động

1. **Scheduler chạy mỗi X giây** (cấu hình trong `SCHEDULE_INTERVAL`)
2. **Kiểm tra số session mới** từ lần summary cuối
3. **Nếu >= NUMBER_OF_SUMMARY** → Tự động thực hiện summary
4. **Lưu kết quả** vào Redis collection `summary`
5. **Cập nhật metadata** để tracking tiến trình

## 🎛️ Commands tham khảo

```bash
# Setup và start scheduler
./deploy.sh setup
./deploy.sh build
./deploy.sh start scheduler

# Monitoring
./deploy.sh status
./deploy.sh logs scheduler

# Manual operations
./deploy.sh summary
./deploy.sh test

# Maintenance
./deploy.sh backup
./deploy.sh restart scheduler
```
