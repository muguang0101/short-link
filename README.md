# 🚀 Short Link（短链接生成系统）

> 基于 **Flask + Redis** 实现的短链接生成与跳转服务，具备高并发计数、限流与自动过期能力。

## ✨ 核心特性

- ✅ **高性能映射**：自研 Base62 短码生成算法
- ✅ **原子计数**：Redis INCR 实现无锁 PV 统计
- ✅ **访问安全**：IP 限流 + URL 合法性校验
- ✅ **资源回收**：TTL 自动过期，防止冷数据堆积
- ✅ **工程规范**：RESTful API + 统一异常处理

## 🛠 技术栈

| 层级 | 技术 |
|---|---|
| Web 框架 | Flask |
| 数据存储 | Redis |
| 算法 | Base62 编码 |
| 并发控制 | Redis 原子操作 |
| 安全 | IP Rate Limit |

## 📐 系统设计原理

### 1️⃣ 短码生成（Base62）
采用 **自增 ID + Base62** 方案，避免 Hash 冲突，保证短码长度最短。
十进制 ID → Base62 编码

1 → b

10 → k

10000 → 2bI

### 2️⃣ 跳转机制（302 Redirect）
使用 **302 临时重定向**，而非 301，确保每次访问都能经过服务器，便于统计 PV。

### 3️⃣ 高并发计数（INCR）
利用 Redis 单线程模型，通过 `INCR` 实现原子计数，解决并发下计数不准的问题。

### 4️⃣ 限流设计
基于 IP 维度，使用 `INCR + EXPIRE` 实现滑动窗口限流，防止恶意刷接口。

## 📌 API 接口

### 生成短链接
http

POST /api/shorten

Content-Type: application/json

{

"url": "https://www.example.com"

}

**响应**
json

{

"code": 200,

"msg": "success",

"data": {

"short_url": "http://127.0.0.1:5000/abc123"

}

}

### 访问短链接
GET http://127.0.0.1:5000/abc123

## 🧠 关键技术点（面试重点）

- **为什么用 Redis 而不是 MySQL？**
  > Redis KV 结构适合高频读取，INCR 原子操作支持高并发计数。

- **为什么用 302 而不是 301？**
  > 301 会被浏览器缓存，无法统计访问量；302 每次请求服务器，便于数据分析。

- **Base62 相比 Hash 的优势？**
  > Hash 存在碰撞风险，需额外处理；Base62 基于自增 ID，绝对唯一且长度可控。

- **INCR 是否线程安全？**
  > 是。Redis 单线程模型保证 INCR 的原子性，无需加锁。

## 🚀 快速启动
bash

pip install flask redis flask-cors

python app.py

## 📈 后续优化方向

- [ ] Redis 主从 + 哨兵（高可用）
- [ ] 布隆过滤器（防止缓存穿透）
- [ ] Lua 脚本（原子限流）
- [ ] Docker 容器化部署

## 📝 项目总结

本项目通过 **Flask + Redis** 实现了短链接的核心闭环，在保证高性能的同时，兼顾了安全性与资源利用率，具备良好的工程实践价值。