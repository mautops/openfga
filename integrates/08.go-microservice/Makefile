.PHONY: help build run test clean docker-build docker-run fmt lint

# 默认目标
help:
	@echo "可用的 make 命令:"
	@echo "  make build         - 编译项目"
	@echo "  make run           - 运行项目"
	@echo "  make test          - 运行测试"
	@echo "  make clean         - 清理构建文件"
	@echo "  make docker-build  - 构建 Docker 镜像"
	@echo "  make docker-run    - 运行 Docker 容器"
	@echo "  make fmt           - 格式化代码"
	@echo "  make lint          - 代码检查"

# 编译项目
build:
	@echo "编译项目..."
	go build -o bin/main main.go

# 运行项目
run:
	@echo "运行项目..."
	go run main.go

# 运行测试
test:
	@echo "运行测试..."
	go test -v ./...

# 清理构建文件
clean:
	@echo "清理构建文件..."
	rm -rf bin/
	go clean

# 构建 Docker 镜像
docker-build:
	@echo "构建 Docker 镜像..."
	docker build -t openfga-go-microservice:latest .

# 运行 Docker 容器
docker-run:
	@echo "运行 Docker 容器..."
	docker run -d -p 8080:8080 --env-file .env --name openfga-go-service openfga-go-microservice:latest

# 格式化代码
fmt:
	@echo "格式化代码..."
	go fmt ./...

# 代码检查
lint:
	@echo "代码检查..."
	golangci-lint run

# 下载依赖
deps:
	@echo "下载依赖..."
	go mod download

# 更新依赖
update-deps:
	@echo "更新依赖..."
	go get -u ./...
	go mod tidy

# 初始化 OpenFGA
init-fga:
	@echo "初始化 OpenFGA..."
	@echo "请确保 OpenFGA 服务已启动"
	@echo "访问 http://localhost:8080 创建 Store 和 Model"
