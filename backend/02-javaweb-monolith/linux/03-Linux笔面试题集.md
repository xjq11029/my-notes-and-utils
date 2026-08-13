# Linux 笔面试题集

> 适用岗位：后端开发 / 运维工程师 / SRE  
> 覆盖范围：文件操作 · 权限管理 · 进程管理 · 网络排查 · Shell 脚本 · 服务部署  
> 难度标注：★ 基础 / ★★ 进阶 / ★★★ 高级

> 📖 **参考链接**：
> - [Linux man pages 在线手册](https://man7.org/linux/man-pages/) -- man7.org 官方手册页，按章节查询命令、系统调用、配置文件格式
> - [systemd 官方文档](https://systemd.io/) -- systemd 项目官方站点，含 service unit、bootup 流程、journal 等
> - [bash(1) 手册页](https://man7.org/linux/man-pages/man1/bash.1.html) -- Bash Shell 完整参考（变量、参数、条件、循环、重定向）
> - [explainshell.com](https://explainshell.com/) -- 命令参数在线解析工具，输入命令即解释每个参数含义

---

## 第一部分：选择题（共 15 题）

---

### 1. 文件操作 ★

在 Linux 中，以下哪个命令可以列出当前目录下所有文件（包括隐藏文件）的详细信息？

A. `ls -a`  
B. `ls -l`  
C. `ls -al`  
D. `ls -i`

**正确答案：C**

**解析：**
- `ls -a`：列出所有文件（含隐藏文件），但不显示详细信息。
- `ls -l`：以长格式显示详细信息，但不包含隐藏文件。
- `ls -al`：`-a` 与 `-l` 组合，同时列出隐藏文件并显示详细信息，符合题意。
- `ls -i`：显示文件的 inode 编号，不显示详细信息。

---

### 2. 权限管理 ★

某文件的权限为 `rwxr-xr--`，用数字表示该权限为多少？

A. 754  
B. 744  
C. 764  
D. 654

**正确答案：A**

**解析：**
权限字符串 `rwxr-xr--` 分为三组：
- 所有者（owner）：`rwx` = 4+2+1 = 7
- 所属组（group）：`r-x` = 4+0+1 = 5
- 其他人（others）：`r--` = 4+0+0 = 4

因此数字表示为 **754**。

---

### 3. 进程管理 ★

以下哪个命令可以实时查看系统中进程的 CPU 和内存使用情况？

A. `ps aux`  
B. `top`  
C. `pstree`  
D. `jobs`

**正确答案：B**

**解析：**
- `ps aux`：静态快照，显示当前所有进程信息，不会实时刷新。
- `top`：交互式实时监控工具，默认每 3 秒刷新一次，显示 CPU、内存等动态信息。
- `pstree`：以树状结构展示进程父子关系，不显示资源使用。
- `jobs`：仅显示当前 Shell 会话中的后台作业。

---

### 4. 文件操作 ★★

在 `/home` 目录下查找所有 `.log` 后缀且大于 100MB 的文件，正确的命令是？

A. `find /home -name "*.log" -size +100M`  
B. `find /home -name *.log -size +100M`  
C. `grep -r "*.log" /home | awk '$5>100M'`  
D. `ls /home/*.log | grep "100M"`

**正确答案：A**

**解析：**
- A 正确：`-name` 的模式使用双引号防止通配符被 Shell 提前展开，`-size +100M` 表示大于 100MB。
- B 错误：不加引号时 `*.log` 可能被 Shell 在当前目录展开，导致非预期结果。
- C 错误：`grep` 用于搜索文件内容，而非按文件名和大小筛选文件。
- D 错误：`ls` 无法递归搜索子目录，且 `grep "100M"` 逻辑不严谨。

---

### 5. Shell 脚本 ★★

以下 Shell 脚本的输出是什么？

```bash
#!/bin/bash
var="hello world"
echo '${var}'
```

A. `hello world`  
B. `${var}`  
C. `''`  
D. 报错

**正确答案：B**

**解析：**
Shell 中单引号 `'` 会阻止所有变量展开和转义，单引号内的内容会原样输出。因此 `${var}` 被当作普通字符串输出，而不是变量值。若改为双引号 `"${var}"`，则输出 `hello world`。

---

### 6. 网络排查 ★★

要查看当前系统中所有处于 `LISTEN` 状态的 TCP 端口，应使用哪个命令？

A. `ss -tln`  
B. `ifconfig -a`  
C. `ping localhost`  
D. `nslookup 127.0.0.1`

**正确答案：A**

**解析：**
- `ss -tln`：`-t` 表示 TCP，`-l` 表示 LISTEN 状态，`-n` 表示以数字形式显示端口（不解析服务名），是最常用的端口检查命令。
- `ifconfig -a`：查看网络接口配置，不显示端口监听信息。
- `ping`：检测网络连通性。
- `nslookup`：DNS 查询工具。

> 注：`netstat -tlnp` 也是常用方式，但 `ss` 在现代 Linux 发行版中更推荐使用。

---

### 7. 权限管理 ★★

默认情况下，普通用户创建新文件时的权限由 `umask` 控制。如果 `umask` 值为 `022`，则新创建的文件权限为？

A. 755  
B. 644  
C. 600  
D. 755

**正确答案：B**

**解析：**
- 文件默认最大权限为 666（`rw-rw-rw-`），目录默认最大权限为 777（`rwxrwxrwx`）。
- `umask 022` 表示从默认权限中屏蔽掉 group 的写权限（2）和 others 的写权限（2）。
- 文件权限：666 - 022 = **644**（`rw-r--r--`）。
- 目录权限：777 - 022 = **755**（`rwxr-xr-x`）。

---

### 8. 进程管理 ★★

`kill -9` 和 `kill -15` 的区别是什么？

A. 没有区别，都能终止进程  
B. `-9` 是强制终止，`-15` 是优雅终止  
C. `-15` 是强制终止，`-9` 是优雅终止  
D. `-9` 只能终止 root 进程

**正确答案：B**

**解析：**
- `kill -9`（SIGKILL）：强制终止，操作系统立即杀死进程，进程无法捕获、忽略或做任何清理工作。数据可能丢失。
- `kill -15`（SIGTERM）：默认信号，优雅终止。进程可以捕获该信号，执行清理操作（关闭文件、释放资源等）后再退出。
- 应优先使用 `kill -15`，仅在进程无响应时使用 `kill -9`。

---

### 9. 文件操作 ★★★

关于 Linux 中的 inode，以下说法错误的是？

A. 每个文件都有一个唯一的 inode 编号  
B. inode 中存储了文件的数据内容  
C. 硬链接与原文件共享同一个 inode  
D. 文件系统 inode 耗尽后无法创建新文件

**正确答案：B**

**解析：**
- A 正确：同一文件系统内每个文件有唯一的 inode 编号。
- **B 错误**：inode 存储的是文件的元数据（权限、所有者、大小、时间戳、数据块指针等），**不包含文件名和文件数据内容**。数据内容存储在数据块（data block）中。
- C 正确：硬链接就是多个目录项指向同一个 inode。
- D 正确：inode 耗尽时即使磁盘有剩余空间也无法创建新文件（因为每个文件需要一个 inode）。

---

### 10. Shell 脚本 ★★★

以下 Shell 脚本执行后，`$?` 的值是多少？

```bash
#!/bin/bash
grep "pattern" /nonexistent_file 2>/dev/null
echo $?
```

A. 0  
B. 1  
C. 2  
D. 127

**正确答案：C**

**解析：**
- `$?` 表示上一条命令的退出状态码。
- `grep` 命令的退出码约定：0 = 匹配成功，1 = 未匹配到，**2 = 发生错误**（文件不存在、权限不足等）。
- 此处 `/nonexistent_file` 不存在，`grep` 返回 2。`2>/dev/null` 仅重定向了错误输出，不影响退出码。

---

### 11. 网络排查 ★★★

使用 `tcpdump` 抓取目标端口为 80 的 HTTP 请求包，并保存到文件，正确的命令是？

A. `tcpdump -i eth0 port 80 -w http.pcap`  
B. `tcpdump -i eth0 dst port 80 -w http.pcap`  
C. `tcpdump -i eth0 src port 80 -w http.pcap`  
D. `tcpdump -i eth0 port 80 > http.pcap`

**正确答案：B**

**解析：**
- A 会抓取源端口或目标端口为 80 的所有包，范围过大。
- **B 正确**：`dst port 80` 精确匹配目标端口为 80 的包（即 HTTP 请求包）。
- C 抓取源端口为 80 的包（即 HTTP 响应包），不符合题意。
- D 使用重定向 `>` 输出的是文本格式，不是 pcap 二进制格式，无法用 Wireshark 等工具分析。

---

### 12. 服务部署 ★★★

关于 systemd 服务单元文件，以下说法正确的是？

A. 服务文件必须放在 `/etc/systemd/system/` 目录下  
B. `ExecStart` 指定服务启动命令，可以写多条  
C. `Restart=always` 表示服务无论以何种原因退出都会自动重启  
D. `After=network.target` 表示服务必须在网络启动之前运行

**正确答案：C**

**解析：**
- A 错误：服务文件可放在 `/etc/systemd/system/`（管理员自定义）或 `/usr/lib/systemd/system/`（软件包安装），前者优先级更高。
- B 错误：`ExecStart` 只能有一条（但 `ExecStartPre`、`ExecStartPost` 可以有多条）。
- **C 正确**：`Restart=always` 表示无论服务正常退出还是异常退出，systemd 都会自动重启该服务。
- D 错误：`After=network.target` 表示在网络服务启动**之后**才启动本服务。

---

### 13. 文件操作 ★★

关于软链接（符号链接）与硬链接，以下说法错误的是？

A. 软链接可以跨文件系统，硬链接不能  
B. 删除原文件后，软链接失效，硬链接仍可访问数据  
C. 硬链接可以链接目录  
D. 软链接有自己的 inode

**正确答案：C**

**解析：**
- A 正确：软链接存储的是路径字符串，可跨文件系统；硬链接基于 inode，不能跨文件系统。
- B 正确：软链接指向路径，原文件删除后路径失效；硬链接共享 inode，删除一个链接不影响数据。
- **C 错误**：硬链接**不能链接目录**（防止形成循环引用，破坏文件系统树结构）。软链接可以链接目录。
- D 正确：软链接是独立的特殊文件，有自己的 inode。

---

### 14. 进程管理 ★★★

将一个正在前台运行的进程放到后台并使其继续运行，正确的操作步骤是？

A. 按 `Ctrl+C`，然后执行 `bg`  
B. 按 `Ctrl+Z`，然后执行 `bg`  
C. 按 `Ctrl+D`，然后执行 `fg`  
D. 按 `Ctrl+Z`，然后执行 `fg`

**正确答案：B**

**解析：**
- `Ctrl+Z`：发送 SIGTSTP 信号，**暂停**（suspend）前台进程并将其放入后台。
- `bg` 命令：让后台暂停的进程**继续运行**（在后台）。
- `Ctrl+C`：发送 SIGINT 信号，中断/终止进程，而非暂停。
- `Ctrl+D`：表示 EOF（输入结束），不用于进程控制。
- `fg`：将后台进程调回前台，不符合题意。

> 完整流程：`Ctrl+Z` 暂停 → `bg` 后台继续 → 可用 `jobs` 查看 → 需要时 `fg` 调回前台。

---

### 15. Shell 脚本 ★★★

以下 `awk` 命令的作用是什么？

```bash
awk -F ':' '{print $1, $3}' /etc/passwd | sort -k2 -n
```

A. 按用户名排序输出所有用户  
B. 输出用户名和 UID，按 UID 数值升序排序  
C. 统计系统中用户总数  
D. 输出 UID 大于 1000 的用户名

**正确答案：B**

**解析：**
- `-F ':'`：以冒号为字段分隔符。
- `{print $1, $3}`：输出第 1 列（用户名）和第 3 列（UID）。
- `sort -k2 -n`：按第 2 列（UID）进行数值排序（`-n`），默认升序。
- 因此该命令输出所有用户名和对应 UID，并按 UID 从小到大排序。

---

## 第二部分：简答题（共 8 题）

---

### 1. 文件权限 ★

**题目：** 请解释 Linux 文件权限 `rwx` 分别代表什么含义？对文件和目录的作用有何不同？

**参考答案：**

| 权限 | 含义 | 对文件的作用 | 对目录的作用 |
|------|------|-------------|-------------|
| `r`（read） | 读 | 可读取文件内容（如 `cat`） | 可列出目录内容（如 `ls`） |
| `w`（write） | 写 | 可修改文件内容 | 可在目录中创建/删除文件 |
| `x`（execute） | 执行 | 可作为程序执行 | 可进入目录（如 `cd`），访问目录下文件 |

**关键点：** 目录的 `x` 权限是访问该目录的前提。即使有 `r` 权限，没有 `x` 也无法进入目录。删除文件需要目录的 `w` 权限，而非文件本身的 `w` 权限。

> 📖 **延伸阅读**：[chmod(1) 手册页](https://man7.org/linux/man-pages/man1/chmod.1.html) -- 权限符号与数字模式、SUID/SGID/Sticky Bit 特殊权限位详解；[stat(1) 手册页](https://man7.org/linux/man-pages/man1/stat.1.html) -- 查看文件 inode 元信息（权限、所有者、时间戳）

---

### 2. 软链接与硬链接 ★★

**题目：** 请从存储原理、跨文件系统、对目录的支持、删除原文件后的行为四个维度，对比软链接与硬链接的区别。

**参考答案：**

| 维度 | 软链接（Symbolic Link） | 硬链接（Hard Link） |
|------|------------------------|-------------------|
| **存储原理** | 独立文件，存储目标路径字符串 | 多个目录项指向同一 inode |
| **inode** | 拥有独立的 inode | 与原文件共享同一 inode |
| **跨文件系统** | 支持 | 不支持 |
| **链接目录** | 支持 | 不支持 |
| **删除原文件** | 链接失效（悬空链接） | 数据仍可通过硬链接访问 |
| **创建命令** | `ln -s source target` | `ln source target` |
| **文件大小** | 仅占路径字符串大小 | 不占用额外数据空间 |

**典型应用场景：**
- 软链接：版本切换（如 `/usr/bin/python -> python3.11`）、快捷方式。
- 硬链接：重要文件的备份保护（防止误删）。

> 📖 **延伸阅读**：[symlink(7) 手册页](https://man7.org/linux/man-pages/man7/symlink.7.html) -- 符号链接与硬链接的内核实现原理、inode 机制、跨文件系统限制；[ln(1) 手册页](https://man7.org/linux/man-pages/man1/ln.1.html) -- `ln` 命令创建软硬链接的参数

---

### 3. 进程状态 ★★

**题目：** Linux 进程有哪几种主要状态？请用 `ps` 输出的状态码说明，并解释各状态的含义。

**参考答案：**

| 状态码 | 状态 | 含义 |
|--------|------|------|
| **R** | Running / Runnable | 正在运行或在运行队列中等待 CPU |
| **S** | Sleeping (Interruptible) | 可中断睡眠，等待事件（如 I/O 完成） |
| **D** | Disk Sleep (Uninterruptible) | 不可中断睡眠，通常在等待 I/O（无法被信号杀死） |
| **T** | Stopped | 进程被暂停（如收到 SIGSTOP 信号） |
| **Z** | Zombie | 僵尸进程，已结束但父进程未回收其资源 |
| **X** | Dead | 进程已终止（极少出现） |

**特别关注：**
- **D 状态**：若大量进程处于 D 状态，通常说明 I/O 瓶颈（磁盘或 NFS 问题）。
- **Z 状态**：僵尸进程不占用内存和 CPU，但会占用进程表条目。大量僵尸进程说明父进程未正确处理子进程退出信号，需修复父进程代码。

> 📖 **延伸阅读**：[ps(1) 手册页](https://man7.org/linux/man-pages/man1/ps.1.html) -- `ps` 输出列含义、STAT 状态码详解；[proc(5) 手册页](https://man7.org/linux/man-pages/man5/proc.5.html) -- `/proc/<pid>/` 虚拟文件系统，查看进程状态、内存、文件描述符

---

### 4. Linux 启动流程 ★★★

**题目：** 请简述 Linux 系统从开机到登录提示符的完整启动流程。

**参考答案：**

```
1. BIOS/UEFI 阶段
   ├── 加电自检（POST）
   ├── 选择启动设备
   └── 加载 MBR/GPT 中的引导程序

2. 引导加载程序（Boot Loader）
   ├── GRUB2 加载内核镜像（vmlinuz）
   ├── 加载 initramfs（临时根文件系统）
   └── 将控制权交给内核

3. 内核初始化
   ├── 解压内核并初始化硬件驱动
   ├── 挂载 initramfs 为临时根文件系统
   ├── 加载存储驱动、文件系统模块
   └── 切换到真实根文件系统（pivot_root）

4. init 进程启动（PID 1）
   ├── systemd（主流发行版）或 SysV init
   ├── 读取配置文件（/etc/systemd/system/）
   └── 按依赖关系并行启动服务

5. 服务启动
   ├── 挂载文件系统（/etc/fstab）
   ├── 启动网络服务（network.target）
   ├── 启动系统服务（sshd、crond、rsyslog 等）
   └── 启动用户态服务

6. 登录提示符
   ├── TTY 终端：getty + login
   └── 图形界面：Display Manager（GDM/LightDM/SDDM）
```

> 📖 **延伸阅读**：[systemd bootup 流程](https://systemd.io/BOOTUP/) -- systemd 官方启动流程文档，详述 firmware→bootloader→kernel→initrd→sysinit→basic→default 各阶段；[boot(7) 手册页](https://man7.org/linux/man-pages/man7/boot.7.html) -- Linux 启动流程概述

---

### 5. Shell 脚本 ★★

**题目：** 请解释 Shell 中 `$@` 和 `$*` 的区别，并说明何时使用 `"$@"`。

**参考答案：**

| 变量 | 不加引号 | 加双引号 |
|------|---------|---------|
| `$@` | 每个参数作为独立单词（与 `$*` 相同） | **每个参数保持独立**（保留原始参数边界） |
| `$*` | 每个参数作为独立单词 | **所有参数合并为一个字符串** |

**关键区别示例：**

```bash
#!/bin/bash
# 假设调用：./script.sh "a b" "c d"

echo "--- \$@ ---"
for arg in "$@"; do echo "$arg"; done
# 输出：
# a b
# c d

echo "--- \$* ---"
for arg in "$*"; do echo "$arg"; done
# 输出：
# a b c d
```

**最佳实践：** 在脚本中传递参数时，**始终使用 `"$@"`**，因为它能保留参数的原始边界（包括含空格的参数）。`"$*"` 会将所有参数合并为一个字符串，这通常不是期望的行为。

> 📖 **延伸阅读**：[bash(1) Special Parameters 章节](https://man7.org/linux/man-pages/man1/bash.1.html#SPECIAL_PARAMETERS) -- `$@`、`$*`、`$#`、`$?`、`$$` 等特殊参数的官方定义与引号行为差异

---

### 6. 网络排查 ★★★

**题目：** 某服务监听 8080 端口，但外部无法访问。请描述完整的排查思路。

**参考答案：**

**分层排查流程：**

```
1. 确认服务是否正在监听
   ss -tlnp | grep 8080
   # 检查是否有进程在 0.0.0.0:8080 或 127.0.0.1:8080 监听
   # 注意：127.0.0.1 仅本机可访问！

2. 检查防火墙规则
   # iptables
   iptables -L -n | grep 8080
   # firewalld
   firewall-cmd --list-all
   # 云服务器安全组（阿里云/腾讯云/AWS 等）

3. 本机连通性测试
   curl -v http://localhost:8080
   curl -v http://127.0.0.1:8080
   # 如果本机可通，说明服务正常，问题在网络层

4. 检查网络层
   # 检查路由
   ip route show
   # 从外部机器测试
   telnet <server_ip> 8080
   nc -zv <server_ip> 8080

5. 检查 SELinux（CentOS/RHEL）
   getenforce
   # 临时关闭测试：setenforce 0
   # 查看 SELinux 端口策略：semanage port -l | grep 8080

6. 检查应用程序绑定地址
   # 确认服务绑定的是 0.0.0.0 而非 127.0.0.1
   # 查看应用配置中的 bind/host 参数
```

**常见原因排序：**
1. 服务绑定在 `127.0.0.1` 而非 `0.0.0.0`（最常见）
2. 防火墙/安全组未放行端口
3. SELinux 策略阻止
4. 服务未正常启动或崩溃

> 📖 **延伸阅读**：[ss(8) 手册页](https://man7.org/linux/man-pages/man8/ss.8.html) -- `ss` 命令查看 socket 统计（替代 `netstat`）；[ip(8) 手册页](https://man7.org/linux/man-pages/man8/ip.8.html) -- `ip` 命令管理网卡、地址、路由、邻居表；[tcpdump(8) 手册页](https://man7.org/linux/man-pages/man8/tcpdump.8.html) -- 抓包过滤器表达式（BPF）语法

---

### 7. 服务部署 ★★★

**题目：** 请编写一个 systemd 服务单元文件，用于部署一个 Node.js 应用（启动命令 `node /opt/app/server.js`），要求：服务崩溃自动重启、以普通用户 `appuser` 运行、设置环境变量 `NODE_ENV=production`。

**参考答案：**

```ini
[Unit]
Description=My Node.js Application
After=network.target

[Service]
Type=simple
User=appuser
Group=appuser
WorkingDirectory=/opt/app
Environment=NODE_ENV=production
Environment=PORT=3000
ExecStart=/usr/bin/node /opt/app/server.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

# 安全加固
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

**部署步骤：**
```bash
# 1. 创建服务文件
vim /etc/systemd/system/myapp.service

# 2. 重载 systemd 配置
systemctl daemon-reload

# 3. 启动服务并设置开机自启
systemctl start myapp
systemctl enable myapp

# 4. 检查状态
systemctl status myapp

# 5. 查看日志
journalctl -u myapp -f
```

**关键字段说明：**
- `Restart=always`：无论以何种方式退出都自动重启。
- `RestartSec=10`：重启前等待 10 秒（防止频繁重启）。
- `WantedBy=multi-user.target`：多用户模式启动时加载。
- `NoNewPrivileges=yes`：禁止服务获取新权限（安全加固）。

> 📖 **延伸阅读**：[systemd.service(5) 手册页](https://man7.org/linux/man-pages/man5/systemd.service.5.html) -- service unit 完整字段说明（ExecStart、Restart、User、Environment 等）；[systemctl(1) 手册页](https://man7.org/linux/man-pages/man1/systemctl.1.html) -- `systemctl` 所有子命令与选项

---

### 8. 性能排查 ★★★

**题目：** 服务器负载（load average）持续偏高，但 CPU 使用率不高。请分析可能的原因并给出排查方法。

**参考答案：**

**现象分析：** load average 反映的是**处于 R 状态（运行/等待 CPU）和 D 状态（不可中断睡眠）的进程平均数**。CPU 使用率不高但负载高，说明大量进程处于 D 状态。

**可能原因：**

| 原因 | 特征 | 排查命令 |
|------|------|---------|
| I/O 瓶颈 | 磁盘读写慢，大量进程等待 I/O | `iostat -x 1`、`iotop` |
| NFS 问题 | 网络文件系统响应慢 | `nfsstat -c`、`mount \| grep nfs` |
| 内核锁竞争 | 大量进程争抢同一资源 | `perf top`、`cat /proc/locks` |
| 内存不足导致频繁换页 | swap 使用率高 | `free -h`、`vmstat 1` |
| 大量僵尸进程 | 进程表被占满 | `ps aux \| grep Z`、`top` |

**标准排查流程：**

```bash
# 1. 查看整体负载
top
uptime

# 2. 查看进程状态分布
ps aux | awk '{print $8}' | sort | uniq -c | sort -rn
# 重点关注 D 状态进程数量

# 3. 定位 D 状态进程
ps aux | grep ' D'
# 查看 WCHAN 列了解进程在等待什么

# 4. 检查 I/O 情况
iostat -x 1 5
# 关注 %util（磁盘利用率）和 await（平均等待时间）

# 5. 检查内存和 swap
free -h
vmstat 1 10
# 关注 si/so 列（swap in/out）

# 6. 查看具体进程 I/O
iotop -o
# 或查看 /proc/<pid>/io
cat /proc/$(pgrep -f problematic_process)/io
```

**排查思路总结：**
- **CPU 高**：先 `top` 看哪个进程，再 `top -H -p <pid>` 看哪个线程，最后用 `perf top` 或 `strace -p <pid>` 查系统调用。
- **内存高**：`top` 看 RSS，`/proc/<pid>/smaps` 看内存分布，`pmap -x <pid>` 看映射。
- **I/O 高**：`iostat -x 1` 看 `%util` 和 `await`，`iotop` 看哪个进程读写。
- **网络慢**：`iftop` 看带宽，`tcpdump` 抓包，`ss -s` 看 socket 统计。

> 📖 **延伸阅读**：[top(1) 手册页](https://man7.org/linux/man-pages/man1/top.1.html) -- `top` 交互命令与字段含义（VIRT/RES/SHR、load average、nice）；[vmstat(8) 手册页](https://man7.org/linux/man-pages/man8/vmstat.8.html) -- `vmstat` 查看 CPU、内存、I/O、系统上下文切换；[iostat(1) 手册页](https://man7.org/linux/man-pages/man1/iostat.1.html) -- `iostat` 磁盘 I/O 统计与 `%util`/`await` 含义

---

## 第三部分：场景题（共 2 题）

---

### 场景题 1：线上服务 CPU 飙升 ★★★

> **生活化类比：性能排查工具 = "医生的听诊器与检查仪器"** —— 服务器出问题就像病人就诊，你不能瞎猜，得用工具"体检"。`top` 是听诊器——快速听一眼心跳（load average）和哪个器官在发烧（高 CPU 进程）；`top -H -p <pid>` 是把听诊器移到具体位置，听哪个线程在异动；`vmstat` 是心电图——持续监测 CPU 上下文切换、中断、I/O 等待的波动；`iostat` 是血压计——测磁盘 I/O 是否堵车；`strace -c` 是化验单——统计系统调用的频次和耗时，找出"代谢异常"；`perf top` 是 CT 扫描——看 CPU 时间都花在哪个函数上；`tcpdump` 是胃镜——看网络"消化"了什么包。优秀的运维就像优秀的老中医：先用听诊器快速定位（top），再针对性深入检查（strace/perf），最后对症下药（限流/重启/扩容）。切忌一上来就重启服务——那相当于病人还没检查就打麻药，问题根因永远找不到。

**场景描述：**

某天凌晨，运维监控告警：线上 Python Web 服务（Django）的 CPU 使用率突然飙升至 95% 以上，持续不降。服务部署在 4 核 8G 的云服务器上。你作为值班工程师，需要紧急排查并处理。请描述你的完整排查思路和操作步骤。

**参考答案：**

**第一阶段：快速定位（2-3 分钟）**

```bash
# 1. 确认问题
top -bn1 | head -20
# 查看 load average、CPU 使用率、wa（I/O等待）

# 2. 定位高 CPU 进程
top -c
# 按 P 排序（CPU 降序），记下 PID
# 假设问题进程 PID=12345

# 3. 查看进程详情
ps -p 12345 -o pid,ppid,user,%cpu,%mem,cmd,etime
# 确认进程运行时长、启动命令
```

**第二阶段：深入分析（5-10 分钟）**

```bash
# 4. 查看进程下的线程
top -H -p 12345
# 定位高 CPU 的具体线程

# 5. 分析系统调用
strace -p 12345 -c -f -T
# 统计系统调用耗时分布，查找异常

# 6. 查看进程打开的文件描述符
lsof -p 12345 | wc -l
lsof -p 12345 | grep -E 'sock|TCP|UDP'
# 检查是否有文件描述符泄漏或大量网络连接

# 7. 抓取 JVM/解释器级别的信息（Python 场景）
# 使用 py-spy 或 pyflame 进行采样
py-spy top --pid 12345
# 或使用 GDB 挂载：
gdb -p 12345 -ex "thread apply all bt" -ex "detach" -ex "quit"
```

**第三阶段：应急处理**

```bash
# 方案A：重启服务（快速恢复）
systemctl restart myapp

# 方案B：限制资源（临时止血）
# 使用 cgroup 限制 CPU 使用
systemctl set-property myapp CPUQuota=200%

# 方案C：保留现场再重启
# 先 dump 关键信息
top -bn1 > /tmp/cpu_dump.txt
ps auxf > /tmp/ps_dump.txt
netstat -anp > /tmp/net_dump.txt
# 保留 core dump
gcore 12345
# 再重启
systemctl restart myapp
```

**第四阶段：事后复盘**

| 可能原因 | 排查方向 | 预防措施 |
|---------|---------|---------|
| 死循环 / 无限递归 | 代码 Review、查看堆栈信息 | 添加超时机制、代码审查 |
| 正则表达式灾难性回溯 | 检查近期上线的正则逻辑 | 使用 RE2 等线性时间正则引擎 |
| 数据库慢查询堆积 | 慢查询日志、连接池耗尽 | 添加查询超时、读写分离 |
| 第三方 API 超时重试风暴 | 查看调用链、网络日志 | 熔断降级、指数退避重试 |
| GC 频繁（Java/Go） | GC 日志分析 | 调整 JVM 参数、排查内存泄漏 |

> 📖 **延伸阅读**：[top(1) 手册页](https://man7.org/linux/man-pages/man1/top.1.html) -- `top` 交互命令（P/M-T 排序）、字段含义、load average 解读；[strace(1) 手册页](https://man7.org/linux/man-pages/man1/strace.1.html) -- `strace` 系统调用追踪与统计（`-c` 汇总、`-f` 跟踪子进程）；[perf(1) 手册页](https://man7.org/linux/man-pages/man1/perf.1.html) -- `perf` 性能分析工具（`perf top`/`perf record`/`perf report`）

---

### 场景题 2：磁盘空间不足 ★★★

> **生活化类比：磁盘空间排查 = "仓库盘点"** —— 服务器磁盘像一座大仓库，`df -h` 是看仓库大门上的库存表——"总容量 100 吨，已用 98 吨，剩 2 吨"。但库存表只告诉你满了，不告诉你什么东西占了地方。`du -h --max-depth=1 | sort -rh` 是派仓管员逐层翻仓——先看哪个区域（/var、/home、/opt）最重，再钻进去看哪个货架最重，层层深入直到找到"罪魁祸首"。`find -size +100M` 是直接找"大件物品"（大文件）。但有个隐蔽的坑：`lsof | grep deleted` 是找"已出库但发货单还没销"的货——文件被删了，但进程还开着文件句柄，空间没真正释放（就像货搬走了但系统还记账），重启进程才能销账。`df -i` 是查"货架格子数"（inode）——有时空间够但格子满了（大量小文件），同样存不进新货。所以完整盘点要查两样：空间（`df -h`）和格子（`df -i`）。

**场景描述：**

用户反馈文件上传功能失败，日志显示 "No space left on device"。你登录服务器执行 `df -h` 发现根分区 `/` 使用率 100%。请描述完整的排查思路，并说明如何预防此类问题再次发生。

**参考答案：**

**第一阶段：确认问题范围**

```bash
# 1. 确认磁盘使用情况
df -h
# 定位使用率 100% 的分区

# 2. 同时检查 inode 使用（inode 耗尽也会报 No space）
df -i
# 即使磁盘空间够，inode 耗尽也无法创建新文件
```

**第二阶段：定位大文件/目录**

```bash
# 3. 从根目录开始逐层排查
du -h --max-depth=1 / 2>/dev/null | sort -rh | head -20
# 定位占用最大的目录，然后逐层深入

# 示例：发现 /var 占用最大
du -h --max-depth=1 /var 2>/dev/null | sort -rh | head -10

# 4. 查找大文件（>100MB）
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -20

# 5. 如发现 inode 耗尽，查找大量小文件的目录
for dir in /*; do
    echo "$(find $dir -type f 2>/dev/null | wc -l) $dir"
done | sort -rn | head -10
```

**第三阶段：常见问题定位**

```bash
# 检查已删除但未释放的文件（进程仍持有句柄）
lsof | grep deleted | awk '{print $1, $2, $7}' | sort -k3 -rn | head -20
# 可以重启对应进程释放空间

# 检查日志文件
du -sh /var/log/*
# 清理旧日志
journalctl --vacuum-size=500M
find /var/log -name "*.log.*" -mtime +30 -delete

# 检查 Docker 占用
docker system df
docker system prune -a -f

# 检查临时文件
du -sh /tmp /var/tmp

# 检查 core dump 文件
find / -name "core.*" -type f -size +10M 2>/dev/null
```

**第四阶段：应急清理**

```bash
# 安全清理（按优先级）
# 1. 清理包管理器缓存
apt clean           # Debian/Ubuntu
yum clean all       # CentOS/RHEL

# 2. 清理旧内核
# Debian/Ubuntu
dpkg -l | grep linux-image | awk '{print $2}'
apt autoremove --purge
# CentOS/RHEL
package-cleanup --oldkernels --count=2

# 3. 清理 systemd 日志
journalctl --vacuum-size=200M

# 4. 截断大日志文件（保留最近内容）
tail -n 10000 /var/log/large.log > /tmp/large.log.tmp
mv /tmp/large.log.tmp /var/log/large.log

# 5. 清理已删除句柄
# 重启持有已删除文件的进程
systemctl restart <service_name>
```

**第五阶段：预防措施**

| 措施 | 说明 |
|------|------|
| **日志轮转** | 配置 logrotate，按大小/时间自动轮转压缩 |
| **磁盘监控告警** | 设置阈值告警（如使用率 >85%），接入 Prometheus + Grafana |
| **应用日志规范** | 限制日志级别（生产环境用 INFO/WARN），禁止 debug 日志长期开启 |
| **定期巡检** | 通过 cron 定时任务检查磁盘使用并清理临时文件 |
| **分区规划** | 将 `/var`、`/tmp`、`/home` 单独分区，防止根分区被写满 |
| **Docker 管理** | 定期执行 `docker system prune`，设置日志驱动限制 |

**标准 logrotate 配置示例（`/etc/logrotate.d/myapp`）：**
```conf
/var/log/myapp/*.log {
    daily
    rotate 7
    maxsize 500M
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    dateext
}
```

> 📖 **延伸阅读**：[df(1) 手册页](https://man7.org/linux/man-pages/man1/df.1.html) -- `df` 查看文件系统磁盘空间与 inode 使用（`-h` 人类可读、`-i` inode 统计）；[du(1) 手册页](https://man7.org/linux/man-pages/man1/du.1.html) -- `du` 估算文件/目录磁盘占用（`--max-depth` 递归深度、`-h` 人类可读）；[find(1) 手册页](https://man7.org/linux/man-pages/man1/find.1.html) -- `find` 查找文件（`-size` 按大小、`-mtime` 按时间、`-exec` 执行命令）；[lsof(8) 手册页](https://man7.org/linux/man-pages/man8/lsof.8.html) -- `lsof` 查看打开的文件描述符（含已删除但未释放的文件）；[logrotate(8) 手册页](https://man7.org/linux/man-pages/man8/logrotate.8.html) -- `logrotate` 日志轮转配置指令（daily/rotate/compress/copytruncate 等）

---

## 学习导航栏

### 按难度分类

| 难度 | 题目编号 |
|------|---------|
| ★ 基础 | 选择 1、2、3 · 简答 1 |
| ★★ 进阶 | 选择 4、5、6、7、8、13 · 简答 2、3、5 |
| ★★★ 高级 | 选择 9、10、11、12、14、15 · 简答 4、6、7、8 · 场景 1、2 |

### 按知识点分类

| 知识点 | 题目编号 |
|-------|---------|
| 文件操作 | 选择 1、4、9、13 · 简答 2 |
| 权限管理 | 选择 2、7 · 简答 1 |
| 进程管理 | 选择 3、8、14 · 简答 3 · 场景 1 |
| 网络排查 | 选择 6、11 · 简答 6 |
| Shell 脚本 | 选择 5、10、15 · 简答 5 |
| 服务部署 | 选择 12 · 简答 7 · 场景 2 |
| 启动流程 | 简答 4 |
| 性能排查 | 简答 8 · 场景 1、2 |

### 推荐学习路径

```
第一周：Linux 基础入门
├── 文件操作（选择 1、4、9、13）
├── 权限管理（选择 2、7 · 简答 1）
└── 软硬链接（简答 2）

第二周：进程与系统管理
├── 进程管理（选择 3、8、14 · 简答 3）
├── 启动流程（简答 4）
└── 服务部署（选择 12 · 简答 7）

第三周：网络与 Shell 脚本
├── 网络排查（选择 6、11 · 简答 6）
├── Shell 脚本（选择 5、10、15 · 简答 5）
└── 综合实战（场景 1、2）

第四周：性能调优与综合复习
├── 性能排查（简答 8）
├── 场景模拟练习
└── 全量刷题自测
```

### 推荐资源

- [Linux 命令行与 Shell 脚本编程大全](https://www.linuxcommand.org/) - 经典入门书籍
- [The Linux Documentation Project](https://tldp.org/) - 官方文档集合
- [Brendan Gregg 性能分析](https://www.brendangregg.com/linuxperf.html) - 性能调优权威参考
- [systemd 官方文档](https://systemd.io/) - systemd 全面指南
- [explainshell.com](https://explainshell.com/) - 命令参数在线解析

---

> **文档版本：** v1.0  
> **最后更新：** 2026-06-30  
> **适用岗位：** 后端开发工程师 / 运维工程师 / SRE / DevOps

> - 返回 [学习路线总览](../../README.md)