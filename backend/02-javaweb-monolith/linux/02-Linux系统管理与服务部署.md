# Linux 系统管理与服务部署

> 学习路线对应：第 11 周 -- Linux 基础
> 前置知识：Linux 基本命令（ls、cd、mkdir、rm、cp、mv、cat、grep、find 等）
> 预计学习时间：3 天

> 📖 **参考链接**：
> - [systemd 官方文档](https://systemd.io/) -- systemd 项目官方站点，涵盖 unit 文件、service、target、journal 等核心概念
> - [systemd.service 手册页](https://man7.org/linux/man-pages/man5/systemd.service.5.html) -- `.service` 单元文件完整字段说明（ExecStart、Restart、User 等）
> - [systemctl 手册页](https://man7.org/linux/man-pages/man1/systemctl.1.html) -- `systemctl` 命令所有子命令与选项
> - [journalctl 手册页](https://man7.org/linux/man-pages/man1/journalctl.1.html) -- `journalctl` 日志查询命令参考
> - [Linux man pages 在线手册](https://man7.org/linux/man-pages/) -- man7.org 官方手册，按章节查询命令、系统调用、配置文件

---

## 一、核心概念

### 1.1 Linux 系统管理全景图

Linux 系统管理是后端工程师的必备技能，涵盖六大核心领域：

```
Linux 系统管理
├── 用户与权限管理  ── 谁能访问、能做什么
├── 进程管理        ── 什么在运行、运行得怎么样
├── 网络管理        ── 如何通信、如何保护
├── 软件包管理      ── 如何安装、升级、卸载
├── 服务部署        ── 如何让应用跑起来
└── 系统监控        ── 系统是否健康、日志在哪
```

| 管理领域 | 核心命令 | 用途 |
|----------|----------|------|
| **用户与权限** | `useradd`、`chmod`、`chown`、`sudo` | 控制访问与操作权限 |
| **进程管理** | `ps`、`top`、`kill`、`systemctl` | 查看和管理运行中的进程 |
| **网络管理** | `ip`、`ss`、`curl`、`firewalld`、`SSH` | 配置网络、调试连接、防火墙 |
| **软件包管理** | `yum`（RHEL/CentOS）、`apt`（Debian/Ubuntu） | 安装、升级、卸载软件 |
| **服务部署** | JDK 多版本切换、MySQL/Redis 安装、Jar 包部署 | 将 Java 应用部署到生产环境 |
| **系统监控** | `df`、`free`、`lsof`、`journalctl`、`crontab` | 监控磁盘、内存、文件、日志、定时任务 |

> 记忆口诀："用户管权限，进程管运行，网络管通信，包管管安装，部署管应用，监控管健康"

---

### 1.2 Linux 用户与权限模型速览

Linux 是一个**多用户、多任务**操作系统，所有资源访问都基于用户身份和权限：

```
用户（User）  ── 属于 ──> 用户组（Group）  ── 拥有 ──> 文件/目录
                                                      │
                                    r（读）w（写）x（执行）
                                    ├── 所有者（Owner）
                                    ├── 所属组（Group）
                                    └── 其他人（Others）
```

**权限数字表示法：**

| 权限 | 字母 | 二进制 | 数字 |
|------|------|--------|------|
| 读 | r | 100 | 4 |
| 写 | w | 010 | 2 |
| 执行 | x | 001 | 1 |

```
示例：chmod 755 file
7 = rwx（所有者：读+写+执行）
5 = r-x（所属组：读+执行）
5 = r-x（其他人：读+执行）
```

---

### 1.3 进程管理模型

Linux 中一切皆进程。每个进程拥有：

| 属性 | 说明 | 查看方式 |
|------|------|----------|
| **PID** | 进程唯一标识符 | `ps aux`、`top` |
| **PPID** | 父进程 ID | `ps -ef` |
| **UID/GID** | 运行进程的用户/组 | `ps -eo pid,user,group,comm` |
| **状态** | R（运行）、S（睡眠）、D（不可中断睡眠）、Z（僵尸）、T（停止） | `ps aux` 的 STAT 列 |
| **优先级** | Nice 值（-20 到 19，越小优先级越高） | `top` 的 NI 列 |

**进程状态流转图：**

```
创建（fork） -> 就绪（R） -> 运行（R） -> 终止（exit）
                  ^            |
                  |            v
                  └── 睡眠（S/D）<── 等待事件
```

---

### 1.4 systemd 与服务管理

现代 Linux 发行版（CentOS 7+、Ubuntu 16.04+）使用 **systemd** 作为初始化系统，`systemctl` 是其管理工具。

> **生活化类比：systemd = "公司的行政管家"** —— 老式 init 系统（SysV init）像个笨拙的老管家：早上上班（开机）时严格按编号顺序一个个叫醒员工（串行启动服务），ssh 不起来就不叫 network，慢得要命；员工晕倒了（服务崩溃）他也不管，等你发现再处理。systemd 是个精明的新管家：一上班就同时给多个部门派活（并行启动，按依赖关系调度），谁先就绪谁就工作；员工晕倒了立即找人顶替（`Restart=on-failure` 自动重启）；所有员工的工作日志统一收进档案室（`journalctl` 统一日志）；还能控制每个员工用的水电额度（Cgroups 资源限制）。`systemctl` 就是你给管家下指令的对讲机：`start`、`stop`、`enable`（设为常驻）、`status`（查勤）。`/etc/systemd/system/*.service` 文件是"员工档案"，写明岗位、汇报关系（`After=/Requires=`）、出了问题怎么办（`Restart=`）。

| systemd 概念 | 说明 | 类比 |
|-------------|------|------|
| **Unit** | 系统管理的抽象单元 | 配置文件 |
| **Service** | 一种 Unit，表示后台服务 | 服务的"启动脚本" |
| **Target** | 一组 Unit 的集合 | 运行级别（Runlevel） |
| **Socket** | 进程间通信的套接字 | 端口监听 |

**systemctl 常用操作：**

```bash
systemctl start nginx      # 启动服务
systemctl stop nginx       # 停止服务
systemctl restart nginx    # 重启服务
systemctl reload nginx     # 重新加载配置（不中断服务）
systemctl enable nginx     # 设置开机自启
systemctl disable nginx    # 取消开机自启
systemctl status nginx     # 查看服务状态
systemctl is-active nginx  # 检查服务是否运行
systemctl list-units --type=service  # 列出所有服务
```

---

## 二、底层原理

### 2.1 用户与权限管理深入

#### 2.1.1 用户与组管理命令

**useradd -- 创建用户：**

```bash
# 基本创建
useradd zhangsan

# 完整创建（指定家目录、Shell、UID、组）
useradd -d /home/zhangsan -s /bin/bash -u 1001 -g developers zhangsan

# 常用参数
# -d  指定家目录
# -s  指定登录 Shell
# -u  指定 UID
# -g  指定主组
# -G  指定附加组
# -m  自动创建家目录
# -M  不创建家目录
```

**用户管理常用命令：**

| 命令 | 用途 | 示例 |
|------|------|------|
| `useradd` | 创建用户 | `useradd -m -s /bin/bash appuser` |
| `userdel` | 删除用户 | `userdel -r appuser`（-r 同时删除家目录） |
| `usermod` | 修改用户属性 | `usermod -aG docker appuser`（追加到 docker 组） |
| `passwd` | 设置/修改密码 | `passwd appuser` |
| `id` | 查看用户 UID/GID | `id appuser` |
| `su` | 切换用户 | `su - appuser`（- 加载目标用户环境） |
| `groupadd` | 创建用户组 | `groupadd developers` |
| `groupdel` | 删除用户组 | `groupdel developers` |

**关键文件：**

| 文件 | 内容 | 格式 |
|------|------|------|
| `/etc/passwd` | 用户账号信息 | `用户名:x:UID:GID:描述:家目录:Shell` |
| `/etc/shadow` | 加密密码 | `用户名:加密密码:最后修改:最小:最大:警告:不活动:过期:保留` |
| `/etc/group` | 用户组信息 | `组名:x:GID:成员列表` |

#### 2.1.2 chmod -- 修改文件权限

```bash
# 数字模式（推荐）
chmod 755 script.sh      # rwxr-xr-x
chmod 644 config.txt     # rw-r--r--
chmod 600 id_rsa         # rw-------（私钥文件专用）

# 符号模式
chmod u+x script.sh      # 给所有者添加执行权限
chmod g-w file.txt       # 移除所属组的写权限
chmod o= file.txt        # 清除其他人的所有权限
chmod a+r file.txt       # 所有人添加读权限

# 递归修改
chmod -R 755 /opt/app/   # 递归修改目录及其所有子文件
```

**常见权限场景：**

| 场景 | 权限 | 数字 | 说明 |
|------|------|------|------|
| 可执行脚本 | `-rwxr-xr-x` | 755 | 所有者可写，其他人只读+执行 |
| 配置文件 | `-rw-r--r--` | 644 | 所有者可写，其他人只读 |
| 私钥文件 | `-rw-------` | 600 | 仅所有者可读写 |
| 共享目录 | `drwxrwxr-x` | 775 | 同组可写，其他人可读+进入 |
| 临时目录 | `drwxrwxrwt` | 1777 | 粘滞位（sticky bit），仅文件所有者可删除 |

#### 2.1.3 chown -- 修改文件归属

```bash
# 修改所有者
chown appuser app.jar

# 修改所有者和所属组
chown appuser:appgroup app.jar

# 仅修改所属组
chown :appgroup app.jar

# 递归修改
chown -R appuser:appgroup /opt/app/
```

#### 2.1.4 sudo -- 提权执行

`sudo` 允许普通用户以 root 或其他用户身份执行命令。

**配置 sudo 权限（`/etc/sudoers`，通过 `visudo` 编辑）：**

```bash
# 允许 appuser 执行所有命令
appuser  ALL=(ALL)       ALL

# 允许 appuser 无密码执行 systemctl 命令
appuser  ALL=(ALL)       NOPASSWD: /usr/bin/systemctl

# 允许 developers 组成员执行所有命令
%developers  ALL=(ALL)   ALL
```

**sudo 工作原理：**
1. 用户执行 `sudo command`。
2. 系统检查 `/etc/sudoers` 中该用户是否被授权。
3. 若授权，要求输入**用户自己的密码**（非 root 密码）。
4. 验证通过后，以 root 身份执行命令。
5. 执行记录写入 `/var/log/secure`（安全审计）。

#### 2.1.5 SUID、SGID 与 Sticky Bit

| 特殊权限 | 数字 | 字母 | 作用于文件 | 作用于目录 |
|----------|------|------|-----------|-----------|
| **SUID** | 4 | u+s | 以文件**所有者**身份执行（如 `passwd` 命令） | 无意义 |
| **SGID** | 2 | g+s | 以文件**所属组**身份执行 | 目录下新建文件继承目录的所属组 |
| **Sticky Bit** | 1 | o+t | 无意义（旧版 Linux 有） | 仅文件**所有者**和 root 能删除文件（如 `/tmp`） |

```bash
# 设置 SUID
chmod u+s /usr/bin/passwd   # 普通用户修改密码时需要访问 /etc/shadow

# 设置 SGID（目录）
chmod g+s /shared/project/  # 该目录下创建的文件自动继承 project 组

# 设置 Sticky Bit
chmod o+t /tmp              # 防止用户删除其他人的临时文件

# 数字模式（SUID+SGID+Sticky）
chmod 4755 file   # SUID + rwxr-xr-x
chmod 2755 dir    # SGID + rwxr-xr-x
chmod 1777 /tmp   # Sticky + rwxrwxrwx
```

> **安全警示**：SUID 程序是常见安全漏洞来源。定期检查系统中的 SUID 文件：`find / -perm -4000 -type f 2>/dev/null`

---

### 2.2 进程管理深入

> **生活化类比：进程管理 = "城市交通指挥"** —— 进程像城市里跑的车，PID 是车牌号，PPID 是车主（父进程）。`ps aux` 是拍一张全城交通照片（快照），`top` 是实时交通监控大屏。车的状态对应：R 是正在路上跑或等红绿灯（运行/就绪）、S 是停在停车场等乘客（可中断睡眠，等 I/O）、D 是进了修车厂不可打断（不可中断睡眠，等磁盘）、Z 是报废了但车牌没注销（僵尸进程，父进程没回收）、T 是被交警叫停（SIGSTOP 暂停）。`kill -15` 是交警礼貌地敲窗"请靠边停车"（优雅终止，进程能收拾东西再走），`kill -9` 是直接拖车强制清走（进程来不及收拾，可能丢数据）。`nice` 值是优先级——消防车（nice=-20）一路绿灯，三轮车（nice=19）遇让就让。`top` 里的 load average 是"当前拥堵指数"，超过车道数（CPU 核心数）就说明堵车了。僵尸进程（Z）像报废车占着车牌号不释放，多了就发不出新车（无法 fork 新进程），得让车主（父进程）去注销，或直接把车主也干掉。

#### 2.2.1 ps -- 查看进程快照

```bash
# BSD 风格（常用）
ps aux                  # 显示所有进程的详细信息

# Unix 风格
ps -ef                  # 显示所有进程的完整格式
ps -eo pid,ppid,user,%cpu,%mem,comm  # 自定义输出列

# 常用组合
ps aux | grep java      # 查找 Java 进程
ps -ef | grep nginx     # 查找 Nginx 进程
ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -10  # 按 CPU 占用排序 Top 10
```

**ps aux 输出列含义：**

| 列 | 含义 | 说明 |
|----|------|------|
| USER | 进程所有者 | 哪个用户启动的 |
| PID | 进程 ID | 唯一标识 |
| %CPU | CPU 使用率 | 单核百分比 |
| %MEM | 内存使用率 | 物理内存百分比 |
| VSZ | 虚拟内存大小 | 单位 KB |
| RSS | 常驻内存大小 | 实际物理内存，单位 KB |
| TTY | 终端 | ? 表示无终端（守护进程） |
| STAT | 进程状态 | R/S/D/Z/T |
| START | 启动时间 | 进程开始运行的时间 |
| TIME | CPU 累计时间 | 进程消耗的 CPU 总时间 |
| COMMAND | 命令 | 启动命令 |

**STAT 状态详解：**

| 状态 | 含义 | 典型场景 |
|------|------|----------|
| R | Running，运行中或可运行 | 正在占用 CPU 或等待 CPU 调度 |
| S | Sleeping，可中断睡眠 | 等待事件（如网络 I/O、定时器） |
| D | Disk Sleep，不可中断睡眠 | 等待磁盘 I/O（通常几毫秒） |
| Z | Zombie，僵尸进程 | 子进程已退出但父进程未回收 |
| T | Stopped，停止 | 被 SIGSTOP 暂停 |
| **附加标记** | | |
| `<` | 高优先级 | Nice 值 < 0 |
| `N` | 低优先级 | Nice 值 > 0 |
| `l` | 多线程 | 包含多个线程 |
| `s` | 会话领导者 | 通常是 Shell 或守护进程 |
| `+` | 前台进程组 | 在前台运行 |

#### 2.2.2 top -- 实时进程监控

```bash
top                     # 默认按 CPU 使用率排序

# 常用交互命令（在 top 界面内按）
# 1    显示每个 CPU 核心的使用情况
# M    按内存使用率排序
# P    按 CPU 使用率排序
# T    按运行时间排序
# k    杀死进程（输入 PID 和信号）
# q    退出 top
# c    切换显示完整命令行
# E    切换内存单位（KB/MB/GB）

# 命令行参数
top -p 1234             # 只监控指定 PID 的进程
top -u appuser          # 只显示指定用户的进程
top -b -n 1             # 批处理模式，输出一次后退出（适合脚本）
```

**top 输出区域解读：**

```
第一行（uptime）：当前时间 运行时长 登录用户数 负载均值(1min/5min/15min)
第二行（tasks）：  进程总数 运行中 睡眠中 停止 僵尸
第三行（CPU）：     us(用户态) sy(内核态) ni(nice) id(空闲) wa(IO等待) hi(硬中断) si(软中断) st(虚拟机偷取)
第四行（内存）：   物理内存总量 已用 空闲 缓冲区
第五行（交换）：   交换区总量 已用 空闲 缓存
```

> **负载均值**：1、5、15 分钟的平均负载。单核 CPU 的理想负载是 1.0，4 核 CPU 的理想负载是 4.0。长期超过 CPU 核心数说明系统过载。

#### 2.2.3 kill -- 发送信号控制进程

```bash
# 信号列表
kill -l                  # 列出所有信号

# 常用信号
kill -15 PID             # SIGTERM：优雅终止（默认），允许进程清理资源
kill -9 PID              # SIGKILL：强制杀死，进程无法捕获
kill -2 PID              # SIGINT：相当于 Ctrl+C
kill -1 PID              # SIGHUP：重新加载配置（常用于守护进程重启）
kill -0 PID              # 信号 0：检查进程是否存在（不发送任何信号）

# 按名称杀进程
killall -15 java         # 杀死所有名为 java 的进程
pkill -f "spring-boot"   # 按命令行模式匹配杀进程
```

**SIGTERM vs SIGKILL：**

| 对比 | SIGTERM（15） | SIGKILL（9） |
|------|--------------|-------------|
| 进程能否捕获 | 能 | 不能 |
| 是否清理资源 | 是（进程自行清理） | 否（内核强制终止） |
| 使用场景 | 正常关闭服务 | 进程无响应时的最后手段 |
| 推荐顺序 | 先发 TERM，等待几秒 | 仍不退出再发 KILL |

---

### 2.3 网络管理深入

#### 2.3.1 ip -- 现代网络配置工具

`ip` 命令已取代传统的 `ifconfig`，功能更强大。

```bash
# 查看网络接口
ip addr show             # 显示所有网络接口的 IP 地址（等价于 ip a）
ip link show             # 显示所有网络接口的链路状态

# 查看路由表
ip route show            # 显示路由表
ip route get 8.8.8.8     # 查询到目标 IP 的路由

# 查看 ARP 表
ip neigh show            # 显示 ARP 缓存

# 查看网络统计
ip -s link show eth0     # 显示 eth0 的详细统计（收发包、错误、丢包）
```

#### 2.3.2 ss -- Socket 统计

`ss` 是 `netstat` 的现代替代品，速度更快，信息更丰富。

```bash
# 查看监听端口
ss -tlnp                 # TCP 监听端口（-t TCP, -l 监听, -n 数字, -p 进程）
ss -ulnp                 # UDP 监听端口

# 查看所有连接
ss -tan                  # 所有 TCP 连接（包括 LISTEN/ESTABLISHED/TIME_WAIT）

# 按状态过滤
ss -tan state established  # 只看已建立的连接
ss -tan state time-wait    # 只看 TIME_WAIT 状态的连接

# 查看连接统计
ss -s                    # 汇总统计

# 常用场景
ss -tlnp | grep 8080    # 查看 8080 端口被哪个进程占用
ss -tan | grep ESTAB    # 查看当前有多少活跃连接
```

**TCP 连接状态说明：**

| 状态 | 含义 | 说明 |
|------|------|------|
| LISTEN | 监听中 | 服务器等待客户端连接 |
| ESTABLISHED | 已建立 | 连接正常通信中 |
| TIME_WAIT | 等待关闭 | 主动关闭方等待 2MSL 后释放 |
| CLOSE_WAIT | 等待关闭 | 被动关闭方等待应用层调用 close() |
| SYN_SENT | 已发送 SYN | 客户端发起连接 |
| SYN_RECV | 已收到 SYN | 服务器收到连接请求 |

#### 2.3.3 curl -- HTTP 调试利器

```bash
# GET 请求
curl http://localhost:8080/api/health
curl -v http://localhost:8080/api/health              # 显示详细信息（请求头+响应头）

# 常用选项
curl -I https://www.example.com                        # 只获取响应头（HEAD 请求）
curl -X POST http://localhost:8080/api/user \
  -H "Content-Type: application/json" \
  -d '{"name":"zhangsan","age":25}'                    # POST JSON 数据
curl -o file.tar.gz http://example.com/file.tar.gz    # 下载文件到指定名称
curl -O http://example.com/file.tar.gz                # 下载文件（保留远程文件名）
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/  # 只输出 HTTP 状态码
curl -x http://proxy:8080 http://example.com          # 通过代理访问
curl -k https://self-signed.example.com               # 忽略 SSL 证书验证
```

**curl 常用场景：**

| 场景 | 命令 |
|------|------|
| 健康检查 | `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health` |
| 测试接口 | `curl -X POST http://localhost:8080/api/order -H "Content-Type: application/json" -d '{}'` |
| 测试超时 | `curl -m 5 http://example.com`（-m 设置最大超时秒数） |
| 下载文件 | `curl -L -o app.tar.gz https://github.com/xxx/releases/latest`（-L 跟随重定向） |

#### 2.3.4 firewalld -- 防火墙管理

```bash
# 基本操作
systemctl start firewalld      # 启动防火墙
systemctl enable firewalld     # 设置开机自启
firewall-cmd --state           # 查看防火墙状态

# 查看规则
firewall-cmd --list-all         # 查看当前区域的完整配置
firewall-cmd --list-ports       # 查看所有开放端口
firewall-cmd --list-services    # 查看所有开放服务

# 开放端口
firewall-cmd --add-port=8080/tcp --permanent    # 永久开放 8080 端口
firewall-cmd --add-port=3306/tcp --permanent    # 永久开放 MySQL 端口
firewall-cmd --add-port=6379/tcp --permanent    # 永久开放 Redis 端口
firewall-cmd --reload                           # 重新加载配置（使 permanent 规则生效）

# 临时开放（不写 --permanent，重启后失效）
firewall-cmd --add-port=8080/tcp

# 移除端口
firewall-cmd --remove-port=8080/tcp --permanent
firewall-cmd --reload

# 富规则（高级用法）
firewall-cmd --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" port port="8080" protocol="tcp" accept' --permanent
```

**常见防火墙场景：**

| 场景 | 操作 |
|------|------|
| 部署 Web 应用 | 开放 80/443 端口 |
| 部署 Java 应用 | 开放应用端口（如 8080） |
| 部署 MySQL | 仅开放给内网 IP（不对外开放 3306） |
| 部署 Redis | 仅开放给内网 IP（不对外开放 6379） |

#### 2.3.5 SSH -- 远程连接管理

```bash
# 基本连接
ssh root@192.168.1.100
ssh -p 2222 root@192.168.1.100        # 指定端口（默认 22）

# 密钥登录
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"   # 生成密钥对
ssh-copy-id root@192.168.1.100                           # 复制公钥到服务器
ssh -i ~/.ssh/id_rsa root@192.168.1.100                  # 使用指定私钥连接

# SCP 文件传输
scp app.jar root@192.168.1.100:/opt/app/                 # 上传文件
scp root@192.168.1.100:/opt/app/logs/app.log ./          # 下载文件
scp -r config/ root@192.168.1.100:/opt/app/              # 上传目录

# SSH 隧道
ssh -L 3306:localhost:3306 root@192.168.1.100            # 本地端口转发（访问远程 MySQL）
ssh -R 8080:localhost:8080 root@192.168.1.100            # 远程端口转发（暴露本地服务）

# SSH 配置优化（~/.ssh/config）
Host prod-server
    HostName 192.168.1.100
    User root
    Port 22
    IdentityFile ~/.ssh/id_rsa_prod
```

**SSH 安全加固建议：**

| 措施 | 配置（`/etc/ssh/sshd_config`） | 说明 |
|------|------|------|
| 禁用 root 登录 | `PermitRootLogin no` | 使用普通用户 + sudo |
| 修改默认端口 | `Port 2222` | 减少暴力破解扫描 |
| 禁用密码登录 | `PasswordAuthentication no` | 仅允许密钥登录 |
| 限制登录用户 | `AllowUsers appuser` | 白名单机制 |
| 空闲超时断开 | `ClientAliveInterval 300` | 5 分钟无操作自动断开 |

---

### 2.4 软件包管理深入

#### 2.4.1 yum（RHEL/CentOS/Fedora）

```bash
# 基础操作
yum install nginx          # 安装
yum remove nginx           # 卸载
yum update nginx           # 更新
yum list installed         # 列出已安装的包
yum search nginx           # 搜索包
yum info nginx             # 查看包信息
yum clean all              # 清理缓存

# 查询文件属于哪个包
yum provides /usr/bin/java   # 查找提供该命令的包

# 查看可用更新
yum check-update

# 仅下载不安装
yum install --downloadonly --downloaddir=/tmp nginx

# 安装开发工具组
yum groupinstall "Development Tools"

# 安装 EPEL 仓库（Extra Packages for Enterprise Linux）
yum install epel-release
```

#### 2.4.2 apt（Debian/Ubuntu）

```bash
# 基础操作
apt install nginx          # 安装
apt remove nginx           # 卸载（保留配置文件）
apt purge nginx            # 完全卸载（包括配置文件）
apt update                 # 更新软件包索引
apt upgrade                # 升级所有可升级的包
apt list --installed       # 列出已安装的包
apt search nginx           # 搜索包
apt show nginx             # 查看包信息
apt autoremove             # 自动删除不需要的依赖

# 查找文件属于哪个包
apt install apt-file
apt-file update
apt-file search /usr/bin/java
```

**yum vs apt 对比：**

| 操作 | yum（CentOS/RHEL） | apt（Ubuntu/Debian） |
|------|---------------------|----------------------|
| 安装包 | `yum install nginx` | `apt install nginx` |
| 卸载包 | `yum remove nginx` | `apt remove nginx` |
| 更新索引 | `yum makecache` | `apt update` |
| 升级包 | `yum update` | `apt upgrade` |
| 搜索包 | `yum search nginx` | `apt search nginx` |
| 清理缓存 | `yum clean all` | `apt clean` |
| 适用发行版 | CentOS、RHEL、Fedora | Ubuntu、Debian |

---

### 2.5 系统监控深入

#### 2.5.1 df -- 磁盘空间监控

```bash
# 查看磁盘使用情况
df -h                     # 人类可读格式（GB/MB）
df -i                     # 查看 inode 使用情况（文件数量限制）
df -T                     # 显示文件系统类型

# 重点关注
df -h /                   # 查看根分区使用情况
df -h /opt                # 查看应用分区使用情况

# 输出解读
# Filesystem   Size  Used Avail Use% Mounted on
# /dev/sda1     50G   20G   28G  42% /
```

**磁盘告警阈值：** 使用率超过 80% 需要关注，超过 95% 急需清理。

#### 2.5.2 free -- 内存监控

```bash
# 查看内存使用情况
free -h                   # 人类可读格式
free -h -s 2              # 每 2 秒刷新一次

# 输出解读
#               total   used   free   shared   buff/cache   available
# Mem:           7.6G    2.1G   1.2G   0.5G     4.3G         5.0G
# Swap:          2.0G    0.0G   2.0G
```

**关键指标：**

| 指标 | 含义 | 说明 |
|------|------|------|
| `total` | 总物理内存 | 硬件安装的内存总量 |
| `used` | 已用内存 | 包括进程占用 + 共享内存 |
| `free` | 完全空闲内存 | 未被任何程序使用的内存 |
| `buff/cache` | 缓冲区/缓存 | Linux 会用空闲内存做磁盘缓存，可随时释放 |
| `available` | 可用内存 | **最重要的指标**，表示新进程可用的内存量（已扣除缓存可释放部分） |
| `Swap` | 交换分区 | 使用 Swap 说明物理内存不足，性能下降 |

> **判断内存是否充足**：看 `available` 而非 `free`。Linux 倾向于将空闲内存用于缓存，`free` 小是正常的。`available` 接近 0 才是真的内存不足。

#### 2.5.3 lsof -- 查看打开的文件

Linux 中一切皆文件，`lsof`（List Open Files）是排查问题的利器。

```bash
# 查看端口被哪个进程占用
lsof -i :8080             # 查看 8080 端口占用
lsof -i tcp:3306          # 查看 3306 端口 TCP 连接

# 查看进程打开的文件
lsof -p 1234              # 查看 PID 1234 打开的所有文件
lsof -c java              # 查看名为 java 的进程打开的文件

# 查看用户打开的文件
lsof -u appuser           # 查看 appuser 用户打开的文件

# 查看被删除但仍被占用的文件（磁盘空间未释放）
lsof | grep deleted       # 常见原因：日志文件被删除但进程未重启

# 查看目录正在被哪些进程使用
lsof /opt/app             # 无法卸载目录时使用

# 查看网络连接
lsof -i                   # 查看所有网络连接
lsof -i @192.168.1.100    # 查看与指定 IP 的连接
```

**常见排查场景：**

| 场景 | 命令 | 说明 |
|------|------|------|
| 端口被占用 | `lsof -i :8080` | 找到占用端口的进程 PID |
| 磁盘空间不释放 | `lsof \| grep deleted` | 找到删除后仍占用的文件，重启对应进程 |
| 目录无法卸载 | `lsof /mnt/data` | 找到正在使用该目录的进程 |
| 查看进程打开了哪些日志 | `lsof -p <PID> \| grep log` | 确认日志输出路径 |

#### 2.5.4 journalctl -- 日志管理

`journalctl` 是 systemd 的日志管理工具，统一管理所有 systemd 服务的日志。

```bash
# 基本操作
journalctl -u app                    # 查看指定服务的日志
journalctl -u app -f                 # 实时跟踪日志（类似 tail -f）
journalctl -u app -n 100             # 查看最近 100 行
journalctl -u app --since "2024-01-01 10:00:00" --until "2024-01-01 12:00:00"  # 按时间范围查看

# 按级别过滤
journalctl -u app -p err             # 只看错误级别日志
journalctl -u app -p warning         # 警告及以上级别

# 系统日志
journalctl -k                        # 查看内核日志（dmesg）
journalctl -b                        # 查看本次启动以来的所有日志
journalctl -b -1                     # 查看上一次启动的日志（排查崩溃原因）

# 日志占用空间
journalctl --disk-usage              # 查看日志占用磁盘空间
journalctl --vacuum-size=500M        # 清理日志，保留最近 500MB
journalctl --vacuum-time=7d          # 清理 7 天前的日志
```

**日志级别（优先级）：**

| 级别 | 值 | 含义 |
|------|-----|------|
| emerg | 0 | 系统不可用 |
| alert | 1 | 必须立即处理 |
| crit | 2 | 严重错误 |
| err | 3 | 错误 |
| warning | 4 | 警告 |
| notice | 5 | 正常但重要 |
| info | 6 | 信息 |
| debug | 7 | 调试信息 |

#### 2.5.5 crontab -- 定时任务

```bash
# 编辑当前用户的定时任务
crontab -e

# 查看当前用户的定时任务
crontab -l

# 删除当前用户的定时任务
crontab -r

# 以指定用户身份编辑
crontab -u appuser -e
```

**Cron 表达式格式：**

```
分钟  小时  日期  月份  星期  命令
*     *     *     *     *    command
```

| 字段 | 取值范围 | 说明 |
|------|----------|------|
| 分钟 | 0-59 | 每小时的第几分钟执行 |
| 小时 | 0-23 | 每天的第几小时执行 |
| 日期 | 1-31 | 每月的第几天执行 |
| 月份 | 1-12 | 每年的第几月执行 |
| 星期 | 0-7（0 和 7 都表示周日） | 每周的第几天执行 |

**常用示例：**

```bash
# 每天凌晨 2 点执行数据库备份
0 2 * * * /opt/scripts/backup-db.sh >> /var/log/backup.log 2>&1

# 每小时执行一次日志清理
0 * * * * /opt/scripts/clean-logs.sh

# 每周一凌晨 3 点重启应用
0 3 * * 1 systemctl restart app

# 每 5 分钟执行一次健康检查
*/5 * * * * curl -s http://localhost:8080/health || systemctl restart app

# 每月 1 号凌晨 1 点清理 30 天前的日志
0 1 1 * * find /opt/app/logs -name "*.log" -mtime +30 -delete
```

**Crontab 注意事项：**

| 注意事项 | 说明 |
|----------|------|
| 环境变量 | Cron 的环境变量与登录 Shell 不同，PATH 通常只有 `/usr/bin:/bin`，建议在脚本中使用绝对路径 |
| 日志输出 | 默认输出会发送邮件给用户，建议重定向到文件：`> /var/log/xxx.log 2>&1` |
| 权限 | 检查脚本是否有执行权限：`chmod +x script.sh` |
| 换行符 | 确保脚本文件使用 Unix 换行符（LF），避免 `\r` 导致脚本解析失败 |
| 日志查看 | 查看 cron 执行日志：`grep CRON /var/log/cron` |

---

## 三、实战应用

### 3.1 JDK 多版本安装与切换

```bash
# ===== CentOS/RHEL 安装 JDK（yum 方式）=====
# 搜索可用的 JDK 版本
yum search java | grep openjdk

# 安装 JDK 8
yum install java-1.8.0-openjdk-devel

# 安装 JDK 11
yum install java-11-openjdk-devel

# 安装 JDK 17
yum install java-17-openjdk-devel

# 查看已安装的 JDK 版本
rpm -qa | grep openjdk

# ===== 多版本切换（alternatives 方式）=====
# 注册 JDK 到 alternatives
alternatives --config java      # 交互式选择默认 Java 版本

# 手动设置
alternatives --set java /usr/lib/jvm/java-17-openjdk-17.0.9.0.9-1.el7.x86_64/bin/java

# 验证
java -version
javac -version

# ===== 手动安装 JDK（tar.gz 方式）=====
# 下载 JDK
wget https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz
# 解压到指定目录
tar -xzf jdk-17_linux-x64_bin.tar.gz -C /usr/local/
# 配置环境变量
cat >> /etc/profile.d/jdk.sh << 'EOF'
export JAVA_HOME=/usr/local/jdk-17.0.9
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
EOF
# 生效
source /etc/profile.d/jdk.sh
```

**JDK 环境变量优先级：**

```
/etc/profile  ->  /etc/profile.d/*.sh  ->  ~/.bash_profile  ->  ~/.bashrc
```

> **生产建议**：使用 `alternatives` 管理多版本 JDK，避免手动修改环境变量导致混乱。

---

### 3.2 MySQL 安装与基础配置

#### 3.2.1 CentOS 7 安装 MySQL 8.0

```bash
# 1. 添加 MySQL 官方 YUM 仓库
rpm -Uvh https://dev.mysql.com/get/mysql80-community-release-el7-11.noarch.rpm

# 2. 安装 MySQL Server
yum install mysql-community-server -y

# 3. 启动 MySQL
systemctl start mysqld
systemctl enable mysqld

# 4. 获取临时密码
grep 'temporary password' /var/log/mysqld.log

# 5. 安全初始化
mysql_secure_installation
# 依次操作：输入临时密码 -> 设置新密码 -> 移除匿名用户 -> 禁止 root 远程登录
#          -> 删除 test 数据库 -> 刷新权限表

# 6. 创建应用数据库和用户
mysql -u root -p << 'EOF'
CREATE DATABASE order_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'appuser'@'%' IDENTIFIED BY 'SecurePass123!';
GRANT ALL PRIVILEGES ON order_db.* TO 'appuser'@'%';
FLUSH PRIVILEGES;
EOF

# 7. 配置远程访问（可选，生产环境建议限制 IP）
# 编辑 /etc/my.cnf，注释掉 bind-address 或设置为 0.0.0.0
# 开放防火墙端口
firewall-cmd --add-port=3306/tcp --permanent
firewall-cmd --reload
```

#### 3.2.2 MySQL 基础优化配置

```ini
# /etc/my.cnf 关键配置
[mysqld]
# 基本配置
server-id = 1
port = 3306
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
default-time-zone = '+08:00'

# 连接配置
max_connections = 500                # 最大连接数
max_connect_errors = 100             # 最大连接错误次数
wait_timeout = 600                   # 非交互连接超时（秒）
interactive_timeout = 600            # 交互连接超时（秒）

# InnoDB 配置（影响性能的关键参数）
innodb_buffer_pool_size = 2G         # 缓冲池大小（建议物理内存的 50%-70%）
innodb_log_file_size = 512M          # 重做日志文件大小
innodb_flush_log_at_trx_commit = 2   # 日志刷新策略（2=每秒刷一次，性能与安全平衡）
innodb_file_per_table = ON           # 每表独立表空间

# 慢查询日志（生产环境建议开启）
slow_query_log = ON
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2                  # 超过 2 秒的查询记录
```

**innodb_flush_log_at_trx_commit 取值说明：**

| 值 | 含义 | 数据安全 | 性能 |
|----|------|----------|------|
| 0 | 每秒刷一次日志到磁盘 | 可能丢失 1 秒数据 | 最高 |
| 1 | 每次提交都刷日志到磁盘 | 不丢失数据 | 最低 |
| 2 | 每次提交写日志到 OS 缓存，每秒刷盘 | 可能丢失 1 秒数据（OS 崩溃时） | 较高 |

> **生产建议**：金融类项目设为 1，普通项目设为 2 即可。

---

### 3.3 Redis 安装与基础配置

```bash
# ===== CentOS 7 安装 Redis 7.x =====

# 1. 安装 EPEL 和 Remi 仓库
yum install epel-release -y
yum install https://rpms.remirepo.net/enterprise/remi-release-7.rpm -y

# 2. 启用 Redis 7 模块
yum module enable redis:7 -y

# 3. 安装 Redis
yum install redis -y

# 4. 配置 Redis（/etc/redis.conf）
# 关键配置项：
# bind 127.0.0.1              # 绑定地址（生产环境建议只监听内网 IP）
# port 6379                   # 监听端口
# requirepass your_password   # 设置密码
# maxmemory 2gb               # 最大内存限制
# maxmemory-policy allkeys-lru # 内存淘汰策略
# daemonize yes               # 后台运行

# 5. 启动 Redis
systemctl start redis
systemctl enable redis

# 6. 验证
redis-cli ping                # 返回 PONG 表示正常
redis-cli -a your_password info server  # 查看服务器信息
```

**Redis 内存淘汰策略选择：**

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `noeviction` | 不淘汰，内存满时写入报错 | 不允许数据丢失的场景 |
| `allkeys-lru` | 所有 key 中淘汰最近最少使用的 | **通用缓存场景（推荐）** |
| `volatile-lru` | 有过期时间的 key 中淘汰 LRU | 持久化 key 不能丢失的场景 |
| `allkeys-lfu` | 所有 key 中淘汰最不频繁使用的 | 访问模式差异大的场景 |
| `volatile-lfu` | 有过期时间的 key 中淘汰 LFU | 同上，但保护持久化 key |

---

### 3.4 Java Jar 包部署实战

#### 3.4.1 传统方式部署（nohup）

```bash
# 1. 准备部署目录
mkdir -p /opt/app/{config,logs,bin}

# 2. 上传 jar 包
scp target/app.jar root@server:/opt/app/

# 3. 编写启动脚本（/opt/app/bin/start.sh）
cat > /opt/app/bin/start.sh << 'EOF'
#!/bin/bash
APP_NAME="app"
APP_HOME="/opt/app"
JAR_FILE="$APP_HOME/app.jar"
LOG_FILE="$APP_HOME/logs/app.log"
PID_FILE="$APP_HOME/$APP_NAME.pid"

# JVM 参数
JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=$APP_HOME/logs/"

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "$APP_NAME is already running (PID: $PID)"
        exit 1
    fi
fi

# 启动
nohup java $JAVA_OPTS -jar $JAR_FILE --spring.profiles.active=prod > $LOG_FILE 2>&1 &
echo $! > $PID_FILE
echo "$APP_NAME started (PID: $!)"
EOF

# 4. 编写停止脚本（/opt/app/bin/stop.sh）
cat > /opt/app/bin/stop.sh << 'EOF'
#!/bin/bash
APP_NAME="app"
APP_HOME="/opt/app"
PID_FILE="$APP_HOME/$APP_NAME.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "$APP_NAME is not running"
    exit 0
fi

PID=$(cat "$PID_FILE")
echo "Stopping $APP_NAME (PID: $PID)..."

# 优雅关闭
kill -15 $PID

# 等待最多 30 秒
COUNT=0
while [ $COUNT -lt 30 ]; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "$APP_NAME stopped"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
    COUNT=$((COUNT + 1))
done

# 超时强制关闭
echo "Force killing $APP_NAME..."
kill -9 $PID
rm -f "$PID_FILE"
echo "$APP_NAME force killed"
EOF

# 5. 赋予执行权限
chmod +x /opt/app/bin/start.sh /opt/app/bin/stop.sh
```

#### 3.4.2 systemd 方式部署（推荐）

```bash
# 创建 systemd service 文件
cat > /etc/systemd/system/app.service << 'EOF'
[Unit]
Description=Spring Boot Application
After=network.target mysql.service redis.service
Wants=mysql.service redis.service

[Service]
Type=simple
User=appuser
Group=appgroup
WorkingDirectory=/opt/app
ExecStart=/usr/bin/java -Xms512m -Xmx1024m -XX:+UseG1GC -jar /opt/app/app.jar --spring.profiles.active=prod
ExecStop=/bin/kill -15 $MAINPID
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=app

# 安全限制
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
systemctl daemon-reload
systemctl start app
systemctl enable app

# 查看日志
journalctl -u app -f          # 实时查看日志
journalctl -u app -n 100      # 查看最近 100 行
journalctl -u app --since "2024-01-01" --until "2024-01-02"  # 按时间范围查看
```

**nohup vs systemd 对比：**

| 对比 | nohup 方式 | systemd 方式 |
|------|-----------|-------------|
| 开机自启 | 需额外配置 rc.local | `systemctl enable` 即可 |
| 进程崩溃重启 | 需额外监控脚本 | `Restart=on-failure` 自动重启 |
| 日志管理 | 手动管理日志文件 | `journalctl` 统一管理 |
| 依赖管理 | 手动确保 MySQL/Redis 先启动 | `After=` 和 `Wants=` 声明依赖 |
| 资源限制 | 无法限制 | 支持 CPU/Memory 限制 |
| 推荐场景 | 临时测试 | **生产环境推荐** |

---

### 3.5 服务部署完整流程

**一次完整的 Java 应用部署流程：**

```bash
# ===== 第 1 步：环境准备 =====
# 安装 JDK 17
yum install java-17-openjdk-devel -y
java -version

# 创建应用用户（不要用 root 运行应用）
useradd -m -s /bin/bash appuser

# 创建应用目录
mkdir -p /opt/app/{config,logs,bin}
chown -R appuser:appuser /opt/app/

# ===== 第 2 步：部署应用 =====
# 上传 jar 包
scp app.jar root@server:/opt/app/
chown appuser:appuser /opt/app/app.jar

# 上传配置文件
scp application-prod.yml root@server:/opt/app/config/

# ===== 第 3 步：配置 systemd 服务 =====
# 创建 service 文件（见 3.4.2）

# ===== 第 4 步：配置防火墙 =====
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --reload

# ===== 第 5 步：启动并验证 =====
systemctl start app
systemctl status app

# 健康检查
curl http://localhost:8080/actuator/health

# 查看日志确认启动成功
journalctl -u app -n 50

# ===== 第 6 步：配置日志轮转 =====
cat > /etc/logrotate.d/app << 'EOF'
/opt/app/logs/*.log {
    daily
    rotate 30
    missingok
    notifempty
    compress
    delaycompress
    copytruncate
    dateext
    dateformat -%Y%m%d
}
EOF
```

---

## 四、常见面试题

### 面试题 1：Linux 文件权限 755、644、600 分别代表什么？如何给一个目录设置 SGID 权限并说明其作用？

**答：**

- **755**：所有者 rwx（读写执行），所属组 r-x（读执行），其他人 r-x（读执行）。适用于可执行脚本和目录。
- **644**：所有者 rw-（读写），所属组 r--（只读），其他人 r--（只读）。适用于普通配置文件。
- **600**：所有者 rw-（读写），所属组 ---（无权限），其他人 ---（无权限）。适用于私钥等敏感文件。

**SGID 设置与作用：**

```bash
chmod g+s /shared/project/
# 或数字方式
chmod 2755 /shared/project/
```

SGID 作用于目录时，该目录下新创建的文件和子目录会**自动继承目录的所属组**，而非创建者的默认组。这在多人协作的共享目录中非常有用，确保同组成员都能访问彼此创建的文件。

---

### 面试题 2：SIGTERM（15）和 SIGKILL（9）的区别？为什么推荐先发 SIGTERM？

**答：**

| 对比 | SIGTERM（15） | SIGKILL（9） |
|------|--------------|-------------|
| 能否被进程捕获 | 能 | 不能 |
| 进程能否清理资源 | 能（关闭连接、刷写缓冲区、释放锁等） | 不能（内核直接终止） |
| 子进程处理 | 进程可自行处理 | 子进程可能变成孤儿进程 |

**推荐先发 SIGTERM 的原因：**
1. 给进程**优雅关闭**的机会：释放数据库连接、刷写日志缓冲区、通知注册中心下线等。
2. 避免数据损坏：如果进程正在写文件，SIGKILL 可能导致数据不完整。
3. 防止资源泄漏：SIGKILL 不释放共享内存、信号量等 IPC 资源。

**最佳实践**：先发 SIGTERM，等待 10-30 秒，如果进程仍不退出，再发 SIGKILL。

---

### 面试题 3：如何排查 Linux 服务器 CPU 飙高的问题？

**答：**

**排查步骤：**

```bash
# 1. 查看系统整体负载
top                     # 观察 CPU 使用率、负载均值、wa（IO 等待）

# 2. 找到 CPU 占用最高的进程
top -o %CPU             # 按 CPU 排序，找到高 CPU 进程的 PID

# 3. 查看该进程的线程 CPU 占用
top -H -p <PID>         # 找到 CPU 占用最高的线程 PID

# 4. 将线程 PID 转换为十六进制
printf "%x\n" <线程PID>  # 得到十六进制 nid

# 5. 导出 Java 线程栈
jstack <进程PID> > jstack.log

# 6. 在 jstack 日志中搜索十六进制 nid
grep -A 20 "nid=0x<十六进制值>" jstack.log

# 7. 定位到具体代码行
```

**常见原因：**
- 死循环或无限递归
- GC 频繁（Full GC 频繁导致 CPU 飙高）
- 大量 JSON 序列化/反序列化
- 正则表达式回溯
- 线程上下文切换过多

---

### 面试题 4：Linux 中如何查找被占用的端口？TIME_WAIT 状态过多怎么办？

**答：**

**查找端口占用：**

```bash
# 方法 1：ss（推荐）
ss -tlnp | grep 8080

# 方法 2：lsof
lsof -i :8080

# 方法 3：netstat（旧版）
netstat -tlnp | grep 8080
```

**TIME_WAIT 过多处理：**

TIME_WAIT 是 TCP 正常关闭流程的一部分，主动关闭方在发送最后一个 ACK 后进入 TIME_WAIT，等待 2MSL（约 60 秒）。高并发场景下（如 Nginx 反向代理）可能出现大量 TIME_WAIT。

**解决方案：**

1. **启用 TCP 连接复用（推荐）**：
   ```bash
   # /etc/sysctl.conf
   net.ipv4.tcp_tw_reuse = 1       # 允许复用 TIME_WAIT 连接
   net.ipv4.tcp_timestamps = 1     # 启用时间戳（tw_reuse 的前提）
   sysctl -p
   ```

2. **调整 TIME_WAIT 相关参数**：
   ```bash
   net.ipv4.tcp_fin_timeout = 30   # 缩短 FIN_WAIT2 超时时间
   net.ipv4.tcp_max_tw_buckets = 5000  # 限制 TIME_WAIT 最大数量
   ```

3. **使用长连接**：HTTP Keep-Alive，减少连接创建和关闭频率。

4. **调整 Nginx upstream 配置**：使用 keepalive 连接池。

---

### 面试题 5：systemd 相比传统 init 有什么优势？如何编写一个 systemd service 文件？

**答：**

**systemd 相比 SysV init 的优势：**

| 对比 | SysV init | systemd |
|------|-----------|---------|
| 启动方式 | 串行启动（一个接一个） | 并行启动（按依赖关系同时启动） |
| 依赖管理 | 靠脚本编号顺序 | 显式声明依赖（`After=/Requires=`） |
| 服务监控 | 无内置监控 | 支持进程崩溃自动重启（`Restart=`） |
| 日志管理 | 各自管理日志文件 | 统一 `journalctl` 管理 |
| 资源控制 | 不支持 | 支持 Cgroups 资源限制 |
| 配置格式 | Shell 脚本 | 声明式 `.service` 文件 |

**systemd service 文件关键字段：**

```ini
[Unit]
Description=服务描述
After=network.target           # 在网络启动后启动
Requires=mysql.service         # 强依赖（mysql 启动失败则本服务不启动）
Wants=redis.service            # 弱依赖（redis 启动失败不影响本服务）

[Service]
Type=simple                    # 简单类型，ExecStart 启动的进程即主进程
User=appuser                   # 运行用户
ExecStart=启动命令
ExecStop=停止命令
Restart=on-failure             # 非正常退出时自动重启
RestartSec=10                  # 重启间隔 10 秒

[Install]
WantedBy=multi-user.target     # 多用户模式下启动
```

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 以 root 用户运行 Java 应用 | 安全风险，一旦被攻击可获取 root 权限 | 忽视安全最佳实践 | 创建专用应用用户（`useradd -m appuser`），以 appuser 身份运行 |
| 使用 kill -9 直接杀进程 | 数据丢失、连接泄漏、注册中心未下线 | 未给进程优雅关闭的机会 | 先发 `kill -15`，等待 10-30 秒，仍不退出再发 `kill -9` |
| 防火墙未开放端口 | 外部无法访问应用 | 忘记配置防火墙规则 | 部署后检查：`firewall-cmd --add-port=8080/tcp --permanent` 并 `--reload` |
| 数据库端口对外暴露 | 被暴力破解、数据泄露 | 防火墙配置过于宽松 | MySQL/Redis 只监听内网 IP，或使用防火墙富规则限制来源 IP |
| 未配置日志轮转 | 磁盘被日志文件占满 | 日志文件无限增长 | 配置 `logrotate` 或使用 `journalctl` 的日志大小限制 |
| 未设置 JVM 内存限制 | 容器/OOM Killer 强制杀死进程 | 默认堆内存可能过大 | 设置 `-Xms` 和 `-Xmx`，如 `-Xms512m -Xmx1024m` |
| 使用弱密码或无密码 | 数据库/Redis 被入侵 | 忽视安全配置 | MySQL 使用强密码，Redis 设置 `requirepass` |
| nohup 输出未重定向 | nohup.out 文件不断增长 | 忽略输出重定向 | 使用 `nohup ... > /dev/null 2>&1 &` 或重定向到日志文件 |
| 未设置服务开机自启 | 服务器重启后应用未启动 | 忘记 `systemctl enable` | 部署后执行 `systemctl enable app` |
| 错误修改系统关键文件权限 | 系统命令无法执行、服务异常 | 误操作 `chmod -R 777 /` | 永远不要对 `/usr`、`/etc`、`/bin` 等系统目录递归修改权限。使用 `chmod` 前先确认目标路径 |

---

## 本章学习自检

完成本章学习后，应该能够：

- [ ] 用自己的话解释 Linux 用户（UID/GID）与权限模型（rwx/SUID/SGID/Sticky Bit）、进程状态（R/S/D/Z/T）流转、TCP 连接状态（LISTEN/ESTABLISHED/TIME_WAIT）、yum vs apt 区别
- [ ] 熟练使用 `useradd`、`chmod`、`chown`、`sudo` 进行用户与权限管理
- [ ] 熟练使用 `ps`、`top`、`kill`、`systemctl` 进行进程与服务管理
- [ ] 熟练使用 `ip`、`ss`、`curl`、`firewalld` 进行网络诊断与防火墙配置
- [ ] 独立完成 JDK 多版本安装切换、MySQL 8.0 安装与配置、Redis 7.x 安装与配置
- [ ] 独立完成 Java Jar 包的 systemd 部署（包括编写 service 文件、配置日志轮转、防火墙规则）
- [ ] 使用 `df`、`free`、`lsof`、`journalctl`、`crontab` 进行系统监控
- [ ] 回答常见面试题（文件权限、SIGTERM vs SIGKILL、CPU 飙高排查、端口占用查找、TIME_WAIT 处理、systemd 优势等）
- [ ] 识别并避免常见错误（root 运行应用、kill -9 强制杀进程、端口未开放、日志未轮转、弱密码、未设开机自启等）

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块下一个文件：[03-Linux 笔面试题集](./03-Linux笔面试题集.md)（即将推出）
> - 关联模块：[Docker 核心原理](../docker-k8s/01-Docker核心原理.md)
> - 关联模块：[Nginx 反向代理与负载均衡](../../03-distributed-microservices/nginx/01-Nginx反向代理与负载均衡.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)