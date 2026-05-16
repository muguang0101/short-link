from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import redis
import string
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# ========================
# Redis 配置
# ========================
try:
    r = redis.Redis(
        host='localhost',
        port=6379,
        password=None,
        decode_responses=True
    )
    r.ping()
    print("✅ Redis 连接成功")
except Exception as e:
    print(f"❌ Redis 连接失败: {e}")
    r = None

# ========================
# 常量定义
# ========================
BASE62 = string.digits + string.ascii_letters
LINK_ID_KEY = "link:id"
TTL_SECONDS = 60 * 60 * 24 * 7  # 7天过期
RATE_LIMIT = 10  # 每分钟最多10次

# ========================
# 工具函数
# ========================
def int_to_base62(n: int) -> str:
    """将整数转换为 Base62"""
    if n == 0:
        return BASE62[0]
    res = []
    while n > 0:
        n, r = divmod(n, 62)
        res.append(BASE62[r])
    return "".join(reversed(res))

def is_valid_url(url: str) -> bool:
    """校验 URL 合法性"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def check_rate_limit(ip: str) -> bool:
    """IP 限流检查"""
    key = f"limit:{ip}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)  # 60秒窗口
    return count <= RATE_LIMIT

# ========================
# 路由接口
# ========================

@app.route("/")
def index():
    return "短链接服务已启动 🚀"

# 1️⃣ 生成短链接（POST）
@app.route("/api/shorten", methods=["POST"])
def shorten():
    if r is None:
        return jsonify({"error": "Redis 未连接"}), 500

    ip = request.remote_addr
    if not check_rate_limit(ip):
        return jsonify({"error": "请求过于频繁，请稍后再试"}), 429

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体必须是 JSON"}), 400

    long_url = data.get("url")
    if not long_url or not is_valid_url(long_url):
        return jsonify({"error": "无效的 URL"}), 400

    # 生成短码
    link_id = r.incr(LINK_ID_KEY)
    short_code = int_to_base62(link_id)

    # 存入 Redis（带过期时间）
    r.setex(short_code, TTL_SECONDS, long_url)

    return jsonify({
        "code": 200,
        "msg": "success",
        "data": {
            "long_url": long_url,
            "short_url": f"{request.host_url}{short_code}"
        }
    }), 200

# 2️⃣ 短链接跳转 + PV 统计
@app.route("/<short_code>")
def redirect_to_long(short_code):
    if r is None:
        return "服务器内部错误", 500

    long_url = r.get(short_code)
    if not long_url:
        return "404 短链接不存在", 404

    # PV +1
    r.incr(f"pv:{short_code}")

    return redirect(long_url)

# ========================
# 启动服务
# ========================
if __name__ == "__main__":
    app.run(debug=True)