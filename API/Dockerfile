# 使用官方的 Golang 镜像作为基础镜像
FROM golang:1.17-alpine AS build

# 设置工作目录
WORKDIR /app

# 将本地的代码复制到容器中的工作目录
COPY . .

# 编译 Go 应用程序
RUN go build -o app .

# 使用轻量的 alpine 镜像作为最终镜像
FROM alpine:latest  

# 设置工作目录
WORKDIR /root/ 

# 从构建阶段复制编译后的二进制文件到最终镜像中
COPY --from=build /app/app .

# 暴露应用程序的端口
EXPOSE 8080

# 运行应用程序
CMD ["./app"]
