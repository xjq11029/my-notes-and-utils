# Nginx 性能优化与安全配置 导览

> 定位：五维框架浓缩提炼 02-Nginx性能优化与安全配置.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-Nginx性能优化与安全配置.md)。
> 前置知识：[Nginx反向代理与负载均衡](./01-Nginx反向代理与负载均衡-导览.md)

---

## 一、动静分离架构

### 1.1 什么是动静分离

| 维度 | 内容 |
|------|------|
| 是什么 | 将动态请求与静态资源请求分开处理，由Nginx直出静态、应用服务器处理动态的架构设计。 |
| 能做什么 | 减轻应用服务器压力；提升静态资源响应速度；独立配置静态缓存策略；便于架构扩展。 |
| 怎么用 | 静态资源location用root直出，动态请求location用proxy_pass转发后端。 |
| 原理和工作流程 | Nginx通过location匹配规则将请求分流：静态资源（HTML、CSS、JS、图片等）匹配到本地目录由Nginx直接读取返回，动态请求（API、JSP、PHP等）匹配到proxy_pass转发给后端应用服务器。Nginx基于事件驱动处理静态文件效率远高于应用服务器，应用服务器专注动态逻辑，整体吞吐量提升。 |
| 缺点 | 增加配置复杂度，location规则与资源目录需严格对应；静态与动态资源版本同步需额外机制保障，避免资源不一致。 |

### 1.2 配置示例

本节为配置代码示例，无五维表格。

### 1.3 sendfile 零拷贝优化

| 维度 | 内容 |
|------|------|
| 是什么 | 利用Linux sendfile系统调用在内核空间直接传输文件，减少数据拷贝次数的优化机制。 |
| 能做什么 | 减少用户态与内核态切换；降低CPU占用；提升静态文件传输吞吐量；配合tcp_nopush与tcp_nodelay优化网络传输。 |
| 怎么用 | `sendfile on;` `tcp_nopush on;` `tcp_nodelay on;` |
| 原理和工作流程 | 传统文件传输需经过"磁盘→内核缓冲区→用户空间→内核缓冲区→网卡"四次拷贝与两次上下文切换。sendfile开启后，数据直接在内核空间从文件描述符拷贝到socket，省去用户空间中转，仅需一次拷贝。tcp_nopush将响应头与文件数据合并发送减少报文段，tcp_nodelay禁用Nagle算法立即发送小包。 |
| 缺点 | 仅对静态文件传输有效，动态生成内容无优化；部分平台或场景下sendfile可能与某些驱动不兼容，需测试验证。 |

### 1.4 gzip 压缩优化

| 维度 | 内容 |
|------|------|
| 是什么 | 对HTTP响应内容进行gzip压缩以减少传输体积的优化配置。 |
| 能做什么 | 压缩文本类资源；控制最小压缩体积；设置压缩级别与缓冲；按类型选择性压缩。 |
| 怎么用 | `gzip on;` `gzip_min_length 1k;` `gzip_comp_level 6;` `gzip_types text/plain text/css application/javascript;` |
| 原理和工作流程 | Nginx在响应返回客户端前，对匹配gzip_types的响应体执行gzip压缩。gzip_min_length过滤过小文件避免压缩开销大于收益。gzip_comp_level控制压缩级别（1-9），级别越高压缩率越高但CPU消耗越大。gzip_buffers定义压缩缓冲区大小。压缩后响应头携带Content-Encoding: gzip，浏览器自动解压。 |
| 缺点 | 压缩消耗CPU资源，高并发下可能成为瓶颈；对已压缩格式（JPG、PNG）压缩效果微弱且浪费CPU；级别过高收益递减明显。 |

### 1.5 静态资源缓存

| 维度 | 内容 |
|------|------|
| 是什么 | 通过HTTP缓存头让浏览器缓存静态资源，减少重复请求的优化策略。 |
| 能做什么 | 设置缓存过期时间；控制缓存策略；适配带哈希文件名的长效缓存；区分HTML短缓存。 |
| 怎么用 | `expires 30d;` `add_header Cache-Control "public, immutable";` |
| 原理和工作流程 | Nginx通过expires指令设置Cache-Control的max-age，浏览器在过期前直接使用本地缓存不发请求。文件名带内容哈希（如app.abc123.js）时可设置很长缓存时间，更新时文件名变化触发重新请求。HTML文件缓存时间设置较短或使用no-cache，每次验证避免拿到过期页面。Vary Accept-Encoding区分压缩与未压缩版本的缓存。 |
| 缺点 | 缓存策略配置不当会导致用户拿到过期资源；文件名不带哈希时长缓存难以更新，需配合版本号或手动刷新机制。 |

## 二、HTTPS 配置优化

### 2.1 SSL/TLS 握手流程

| 维度 | 内容 |
|------|------|
| 是什么 | HTTPS建立加密通信时客户端与服务端协商加密参数的交互流程。 |
| 能做什么 | 协商加密套件；交换随机数与密钥材料；验证服务端证书身份；建立会话密钥。 |
| 怎么用 | 完整握手含Client Hello、Server Hello、证书下发、密钥交换、Finished五阶段。 |
| 原理和工作流程 | 客户端发送Client Hello携带支持的加密套件与随机数A；服务端回复Server Hello选择加密套件、返回随机数B与证书；服务端发送密钥交换参数后完成Server Done；客户端验证证书后发送预主密钥；双方基于随机数与预主密钥生成会话密钥，交换Finished消息确认握手完成。TLS 1.2支持缩写握手复用会话，TLS 1.3支持0-RTT减少握手次数。 |
| 缺点 | 完整握手需2-RTT延迟，影响首次访问体验；证书验证与密钥交换计算开销大，高并发下CPU压力显著。 |

### 2.2 HTTPS 基础配置

| 维度 | 内容 |
|------|------|
| 是什么 | Nginx启用HTTPS服务所需的证书、协议、加密套件与会话缓存等核心配置。 |
| 能做什么 | 监听443并启用HTTP/2；指定证书与私钥；限定安全协议版本；配置会话缓存复用；启用HSTS。 |
| 怎么用 | `listen 443 ssl http2;` `ssl_certificate /etc/nginx/ssl/example.com.crt;` `ssl_certificate_key /etc/nginx/ssl/example.com.key;` `ssl_protocols TLSv1.2 TLSv1.3;` |
| 原理和工作流程 | listen指令绑定443端口并启用ssl与http2。ssl_certificate指定公钥证书链，ssl_certificate_key指定私钥。ssl_protocols限定允许的TLS版本，禁用不安全的SSLv3与TLSv1.0/1.1。ssl_ciphers定义加密套件优先级，ssl_prefer_server_ciphers让服务端决定套件。ssl_session_cache开启共享会话缓存避免重复握手。HSTS头强制浏览器后续使用HTTPS访问。 |
| 缺点 | 证书私钥泄露会导致中间人攻击，需严格管控权限；旧客户端不支持TLS 1.2/1.3会被拒绝访问。 |

### 2.3 证书说明

| 维度 | 内容 |
|------|------|
| 是什么 | HTTPS配置中公钥证书与私钥文件的含义与获取方式说明。 |
| 能做什么 | 区分证书链与私钥；选择免费或付费证书来源；指导证书部署。 |
| 怎么用 | `ssl_certificate`指向全链证书，`ssl_certificate_key`指向私钥。 |
| 原理和工作流程 | ssl_certificate应为全链证书（服务器证书+中间证书），保证客户端能完整验证到根CA。ssl_certificate_key为对应私钥，与证书公钥配对用于密钥交换。证书由CA机构签发，Let's Encrypt、ZeroSSL、阿里云等提供免费证书。证书过期后需续期，否则浏览器报错。 |
| 缺点 | 免费证书有效期短（如Let's Encrypt 90天），需配置自动续期；私钥管理不当是常见安全漏洞。 |

### 2.4 HTTP/2 优势

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP/2协议相比HTTP/1.1在传输性能上的核心改进特性。 |
| 能做什么 | 二进制分帧高效解析；多路复用并发请求；HPACK头部压缩；服务端主动推送资源。 |
| 怎么用 | `listen 443 ssl http2;`（Nginx 1.9.5+） |
| 原理和工作流程 | HTTP/2采用二进制分帧层，将请求响应拆分为帧传输，解析效率高于文本格式。多路复用允许同一TCP连接上并行多个请求，消除HTTP/1.1的队头阻塞。HPACK算法对请求头建立索引表与哈夫曼编码压缩，减少重复头部体积。服务端推送可在客户端请求前主动推送关联资源。Nginx通过listen指令的http2参数启用。 |
| 缺点 | 多路复用使单连接承载多请求，TCP丢包会影响所有流；服务端推送配置复杂且浏览器支持逐渐弱化；部分老旧客户端不支持HTTP/2。 |

### 2.5 性能优化要点

| 维度 | 内容 |
|------|------|
| 是什么 | HTTPS场景下降低握手开销与提升传输效率的关键优化项汇总。 |
| 能做什么 | 禁用旧协议；开启会话复用；启用OCSP Stapling减少客户端验证延迟。 |
| 怎么用 | `ssl_session_cache shared:SSL:10m;` `ssl_stapling on;` `resolver 8.8.8.8 1.1.1.1 valid=60s;` |
| 原理和工作流程 | 仅保留TLSv1.2与TLSv1.3避免旧协议安全与性能问题。ssl_session_cache开辟共享内存存储会话参数，客户端复用会话跳过完整握手。ssl_stapling让Nginx预先向CA获取证书吊销状态并缓存，客户端无需自行访问OCSP服务器，降低握手延迟。resolver配置DNS用于OCSP与域名解析。 |
| 缺点 | OCSP Stapling依赖CA响应及时性，CA不可用时回退为不stapling；会话缓存占用共享内存，需合理规划容量。 |

## 三、核心性能优化

### 3.1 worker_processes 进程数配置

| 维度 | 内容 |
|------|------|
| 是什么 | 配置Nginx Worker进程数量的全局指令，决定并发处理能力基础。 |
| 能做什么 | 自动按CPU核心数生成Worker；手动指定进程数；控制每个进程最大文件描述符。 |
| 怎么用 | `worker_processes auto;` `worker_rlimit_nofile 65535;` |
| 原理和工作流程 | worker_processes设定Worker进程数量，auto让Nginx自动检测CPU核心数并设置为相等值，使每个Worker绑定一个核心避免跨核切换。单用途Nginx服务器可设为核心数或核心数×2。worker_rlimit_nofile设定每个Worker可打开的最大文件描述符数，影响最大连接数上限。进程数过多会增加进程切换开销与内存占用。 |
| 缺点 | 设置过大导致进程切换开销增加，反而降低性能；auto依赖CPU亲和性配置，容器化环境可能识别不准确。 |

### 3.2 worker_connections 连接数配置

| 维度 | 内容 |
|------|------|
| 是什么 | events块中配置每个Worker进程最大并发连接数的指令。 |
| 能做什么 | 设定单Worker连接上限；选择epoll事件模型；开启一次性接收所有新连接。 |
| 怎么用 | `events { worker_connections 10240; use epoll; multi_accept on; }` |
| 原理和工作流程 | worker_connections限定每个Worker同时持有的连接数，总并发连接数等于worker_processes乘以worker_connections。use epoll选择Linux下高效事件复用模型，支持水平触发与大量连接。multi_accept开启后Worker一次唤醒接收所有待处理新连接，减少唤醒次数。8核乘以10240可达81920并发连接。 |
| 缺点 | 连接数受系统文件描述符限制（ulimit）约束，需同步调整系统参数；设置过高而流量不足会浪费内存资源。 |

### 3.3 keepalive 长连接优化

| 维度 | 内容 |
|------|------|
| 是什么 | 客户端与Nginx之间保持TCP长连接以复用连接的优化配置。 |
| 能做什么 | 设定长连接空闲超时；限制单连接最大请求数；减少TCP握手开销。 |
| 怎么用 | `keepalive_timeout 65s;` `keepalive_requests 100;` |
| 原理和工作流程 | keepalive_timeout设定连接空闲保持的最长时间，超时后Nginx主动关闭连接。keepalive_requests限定单个连接最多处理的请求数，达到后关闭连接防止长期占用。长连接复用避免每次请求重新TCP三次握手与慢启动，降低连接建立延迟，提升小请求场景的吞吐。 |
| 缺点 | 长连接占用连接资源，高并发下空闲连接过多会消耗连接数配额；timeout过长导致连接资源长期闲置。 |

### 3.4 缓冲区调优

| 维度 | 内容 |
|------|------|
| 是什么 | 对客户端请求与后端响应缓冲区大小进行调优的配置集合。 |
| 能做什么 | 调整请求体与请求头缓冲；配置后端响应缓冲区数量与大小；控制繁忙缓冲阈值。 |
| 怎么用 | `client_body_buffer_size 128k;` `client_header_buffer_size 1k;` `proxy_buffers 8 16k;` `proxy_busy_buffers_size 64k;` |
| 原理和工作流程 | client_body_buffer_size与client_header_buffer_size设定请求体与请求头初始缓冲，超出则写入临时文件。large_client_header_buffers设定大请求头的额外缓冲。proxy_buffering开启后Nginx将后端响应缓存到proxy_buffers再返回客户端，proxy_busy_buffers_size设定繁忙时可直接用于响应的缓冲上限，超出后缓冲写入磁盘。合理调优减少磁盘IO与后端压力。 |
| 缺点 | 缓冲区过大占用内存，过小导致频繁写磁盘或请求被拒；proxy_buffering开启会延迟响应首字节到达客户端。 |

### 3.5 内核参数优化（Linux）

| 维度 | 内容 |
|------|------|
| 是什么 | 在Linux系统层面调整TCP与网络相关内核参数以配合Nginx高并发的优化配置。 |
| 能做什么 | 开启TIME_WAIT复用；增大backlog队列；调大最大连接数；调整TCP超时时间。 |
| 怎么用 | 修改`/etc/sysctl.conf`后执行`sysctl -p`生效。 |
| 原理和工作流程 | tcp_tw_reuse允许TIME_WAIT状态的socket复用于新连接，缓解端口耗尽。somaxconn与netdev_max_backlog增大监听队列与网卡接收队列，避免连接在握手阶段被丢弃。tcp_max_syn_backlog增大SYN队列应对突发连接。tcp_max_tw_buckets限制TIME_WAIT数量防止资源耗尽。tcp_fin_timeout与tcp_keepalive_time缩短连接回收周期。 |
| 缺点 | tcp_tw_recycle在NAT环境会导致连接异常，需谨慎使用；参数调整影响整机网络行为，需充分测试避免副作用。 |

## 四、安全配置实践

### 4.1 隐藏版本号

| 维度 | 内容 |
|------|------|
| 是什么 | 关闭Nginx响应头与错误页中版本号显示的安全配置。 |
| 能做什么 | 避免泄露具体版本；减少针对特定版本的攻击面。 |
| 怎么用 | `server_tokens off;` |
| 原理和工作流程 | server_tokens设为off后，Nginx在Server响应头与默认错误页中只显示nginx而不显示具体版本号。攻击者无法通过版本号精准匹配已知漏洞，降低被自动化扫描工具针对的概率。该指令在http、server、location块均可配置。 |
| 缺点 | 仅隐藏版本号而非彻底消除指纹，专业工具仍可通过其他特征识别Nginx；属于安全加固的浅层措施，需配合其他防护。 |

### 4.2 IP 访问控制

| 维度 | 内容 |
|------|------|
| 是什么 | 基于客户端IP地址进行访问允许或拒绝的访问控制配置。 |
| 能做什么 | 禁止访问敏感目录；限制管理后台仅特定网段访问；按IP黑白名单过滤。 |
| 怎么用 | `location /admin { allow 192.168.1.0/24; deny all; }` |
| 原理和工作流程 | Nginx按allow与deny指令顺序匹配客户端IP，命中即应用对应规则。规则匹配从上到下，首个匹配项生效。常用于保护.git目录、限制后台管理入口仅内网访问。deny all作为兜底拒绝所有未显式允许的IP。规则可在http、server、location、limit_except块中配置。 |
| 缺点 | 基于IP的控制在大规模代理或CDN场景下需依赖X-Forwarded-For，易被伪造；规则维护成本随业务增长上升。 |

### 4.3 限流配置 limit_req_zone

| 维度 | 内容 |
|------|------|
| 是什么 | 基于令牌桶算法对请求速率进行限制的Nginx限流机制。 |
| 能做什么 | 按客户端IP或变量限流；设定平均速率与突发容量；控制突发请求处理策略。 |
| 怎么用 | `limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;` `limit_req zone=perip burst=20 nodelay;` |
| 原理和工作流程 | limit_req_zone在http块定义限流区域，以$binary_remote_addr为key，分配10m共享内存存储状态，rate=10r/s设定每秒10请求的平均速率。limit_req在location启用限流，burst=20允许20个突发请求排队，nodelay表示突发请求立即处理不延迟，超过桶容量则返回503。令牌桶以固定速率生成令牌，请求消耗令牌，桶满则拒绝。 |
| 缺点 | 限流粒度基于单IP，NAT环境下误伤正常用户；rate设置过低会限制正常流量，过高失去保护意义；nodelay下突发仍可能压垮后端。 |

### 4.4 CORS 跨域配置

| 维度 | 内容 |
|------|------|
| 是什么 | Nginx配置跨域资源共享响应头以允许浏览器跨域访问的机制。 |
| 能做什么 | 设置允许来源；配置允许方法与请求头；处理OPTIONS预检请求；支持携带凭证。 |
| 怎么用 | `add_header Access-Control-Allow-Origin $http_origin;` `add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";` |
| 原理和工作流程 | 浏览器跨域请求时先发送OPTIONS预检请求，Nginx通过if判断请求方法为OPTIONS时直接返回204并附加CORS响应头。Access-Control-Allow-Origin指定允许的来源，Access-Control-Allow-Methods限定允许的HTTP方法，Access-Control-Allow-Headers限定允许的请求头，Access-Control-Max-Age控制预检缓存时间。正式请求时Nginx同样附加CORS头。 |
| 缺点 | 使用通配符来源与凭证同时启用存在安全隐患；OPTIONS判断用if指令存在Nginx if陷阱问题，复杂场景需用map优化。 |

### 4.5 其他安全建议

| 维度 | 内容 |
|------|------|
| 是什么 | 防止点击劫持、拦截恶意UA、关闭目录遍历等补充安全加固措施。 |
| 能做什么 | 设置X-Frame-Options防点击劫持；阻止恶意爬虫UA；关闭目录列表防止文件泄露。 |
| 怎么用 | `add_header X-Frame-Options DENY;` `add_header X-Content-Type-Options nosniff;` `autoindex off;` |
| 原理和工作流程 | X-Frame-Options设为DENY禁止页面被iframe嵌套，防止点击劫持攻击。X-Content-Type-Options设为nosniff阻止浏览器MIME嗅探。X-XSS-Protection启用浏览器XSS过滤器。通过if匹配恶意User-Agent返回403拦截爬虫。autoindex off关闭目录列表，防止未授权的文件遍历。 |
| 缺点 | X-Frame-Options为旧标准，现代浏览器更推荐CSP的frame-ancestors；UA拦截规则需持续更新，误判会拒绝正常用户。 |

## 五、避坑指南

本节为常见问题对比汇总表，无五维表格。

## 本章学习自检

本节为自检清单，无五维表格。

---

> [返回原文](./02-Nginx性能优化与安全配置.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
