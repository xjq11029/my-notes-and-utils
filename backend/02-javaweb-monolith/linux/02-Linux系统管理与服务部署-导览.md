# Linux 系统管理与服务部署 导览

> 定位：五维框架浓缩提炼 02-Linux系统管理与服务部署.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-Linux系统管理与服务部署.md)。
> 前置知识：[Linux核心命令与Shell脚本](./01-Linux核心命令与Shell脚本-导览.md)

---

## 一、核心概念

### 1.1 Linux 系统管理全景图

| 维度 | 内容 |
|------|------|
| 是什么 | 涵盖用户权限、进程、网络、软件包、服务部署、系统监控六大领域的管理框架 |
| 能做什么 | 控制访问权限；管理运行进程；配置网络与防火墙；安装升级软件；部署应用服务；监控磁盘内存日志 |
| 怎么用 | `useradd`/`chmod`管权限；`ps`/`top`/`systemctl`管进程；`ip`/`ss`/`firewall-cmd`管网络 |
| 原理和工作流程 | Linux系统管理基于"一切皆文件"与"一切皆进程"两大抽象。用户身份由UID/GID标识，权限以rwx位图存储在inode。进程由内核调度，状态在R/S/D/Z/T间流转。systemd作为PID 1按依赖并行启动服务单元，通过cgroups限制资源，journal统一收集日志 |
| 缺点 | 六大领域命令繁多记忆负担重；不同发行版工具链有差异（yum/apt、netstat/ss）；生产环境误操作风险高，需严格权限控制 |

---

### 1.2 Linux 用户与权限模型速览

| 维度 | 内容 |
|------|------|
| 是什么 | 基于用户、用户组、rwx权限位实现多用户多任务资源访问控制的模型 |
| 能做什么 | 区分所有者、所属组、其他人权限；用数字或符号设置读写执行；实现多用户隔离与协作 |
| 怎么用 | `chmod 755 file`；`chown user:group file`；`id user`查看UID/GID |
| 原理和工作流程 | 每个用户有唯一UID，属于一个主组和若干附加组，信息存于`/etc/passwd`与`/etc/group`。文件inode中记录所有者UID、所属组GID和9位权限位（所有者rwx、组rwx、其他人rwx）。进程访问文件时内核比较进程的UID/GID与文件属主属组，决定套用哪组权限位。rwx对应数字4/2/1，三组相加得三位八进制数 |
| 缺点 | 三类权限粒度粗，无法对单个用户单独授权（需ACL扩展）；权限数字表示新手易算错；root用户不受权限约束存在安全风险 |

---

### 1.3 进程管理模型

| 维度 | 内容 |
|------|------|
| 是什么 | 描述进程属性、状态及状态流转的管理模型 |
| 能做什么 | 标识进程PID/PPID；记录运行用户与优先级；跟踪R/S/D/Z/T状态流转 |
| 怎么用 | `ps aux`；`ps -ef`；`top`查看NI列优先级 |
| 原理和工作流程 | 进程是程序运行的实例，内核为每个进程分配task_struct结构体，记录PID、PPID、UID、状态、调度优先级（Nice值-20到19，越小越优先）。进程经fork创建进入就绪态，被调度器选中运行，等待事件时进入睡眠态S或不可中断D，子进程退出但父进程未回收时变僵尸Z。`ps`读取`/proc`下各进程目录汇总输出 |
| 缺点 | 僵尸进程占用进程表条目不释放；D状态进程无法被信号杀死；Nice值范围有限，精细控制需cgroups |

---

### 1.4 systemd 与服务管理

| 维度 | 内容 |
|------|------|
| 是什么 | 现代Linux的初始化系统与服务管理器，systemctl是其管理工具 |
| 能做什么 | 启动停止重启服务；设置开机自启；声明服务依赖；按Target分组管理单元 |
| 怎么用 | `systemctl start nginx`；`systemctl enable nginx`；`systemctl status nginx`；`systemctl list-units --type=service` |
| 原理和工作流程 | systemd作为PID 1启动，读取`/etc/systemd/system`与`/usr/lib/systemd/system`下的`.service`单元文件，构建依赖图后按`After`/`Requires`/`Wants`关系并行启动服务。每个Service单元由ExecStart指定的进程作为主进程，systemd监控主进程，崩溃时按Restart策略重启。通过cgroups限制资源，通过journald统一收集日志 |
| 缺点 | 单元文件语法有一定学习成本；并行启动依赖声明错误可能导致服务启动顺序异常；日志为二进制格式需journalctl查看，传统文本工具不直接兼容 |

---

## 二、底层原理

### 2.1 用户与权限管理深入

本节为引导性标题，下属子节见下方五维表格。

#### 2.1.1 用户与组管理命令

| 维度 | 内容 |
|------|------|
| 是什么 | useradd、usermod、userdel、groupadd等用户与组管理命令的集合 |
| 能做什么 | 创建删除用户；修改用户属性与所属组；设置密码；切换用户身份 |
| 怎么用 | `useradd -m -s /bin/bash appuser`；`usermod -aG docker appuser`；`passwd appuser`；`su - appuser` |
| 原理和工作流程 | useradd在`/etc/passwd`新增用户行、`/etc/shadow`新增密码行、`/etc/group`新增组行，`-m`创建家目录并复制`/etc/skel`模板。usermod修改passwd与group文件中的属性。passwd调用PAM模块校验后写入加密密码到shadow。su通过setuid切换真实与有效UID，`-`参数同时加载目标用户环境变量 |
| 缺点 | 直接编辑passwd/shadow文件易格式错误导致无法登录；userdel不加`-r`会残留家目录；命令参数较多需查阅文档 |

---

#### 2.1.2 chmod -- 修改文件权限

| 维度 | 内容 |
|------|------|
| 是什么 | 修改文件或目录所有者、组、其他人rwx权限位的命令 |
| 能做什么 | 数字模式设置精确权限；符号模式增减权限；递归修改目录树 |
| 怎么用 | `chmod 755 script.sh`；`chmod u+x file`；`chmod -R 755 /opt/app/` |
| 原理和工作流程 | chmod调用`chmod`系统调用修改inode中的mode字段。数字模式将三组rwx分别转为八进制数组合，如755对应rwxr-xr-x。符号模式按`用户(操作)(权限)`格式增删。`-R`递归遍历目录树对每个文件调用chmod。SUID/SGID/Sticky分别占用八进制首位4/2/1 |
| 缺点 | 递归修改可能误改关键系统文件权限；数字模式需手工计算易出错；对符号链接chmod作用于目标文件 |

---

#### 2.1.3 chown -- 修改文件归属

| 维度 | 内容 |
|------|------|
| 是什么 | 修改文件或目录所有者与所属组的命令 |
| 能做什么 | 更改文件所有者；更改所属组；递归修改目录树归属 |
| 怎么用 | `chown appuser app.jar`；`chown appuser:appgroup file`；`chown -R appuser:appgroup /opt/app/` |
| 原理和工作流程 | chown调用`chown`系统调用修改inode中的UID与GID字段。只有root用户有权执行chown（普通用户可通过sudo提权）。`-R`递归遍历目录树修改每个文件。仅写`:group`表示只改组。修改归属后，原权限位不变但生效对象改变，可能影响访问控制 |
| 缺点 | 递归修改耗时且不可逆，误操作影响服务访问；普通用户无权chown；改属主后可能因权限不匹配导致服务无法读写文件 |

---

#### 2.1.4 sudo -- 提权执行

| 维度 | 内容 |
|------|------|
| 是什么 | 允许普通用户以root或其他用户身份执行命令的提权机制 |
| 能做什么 | 按策略授权特定命令；免密码执行；记录审计日志；支持组级授权 |
| 怎么用 | `sudo command`；`sudo -u appuser command`；`visudo`编辑配置 |
| 原理和工作流程 | sudo程序设置了SUID位，运行时有效UID为root。执行时先读取`/etc/sudoers`策略，校验当前用户是否被授权该命令。授权通过后要求输入用户自己的密码（非root密码），验证成功后fork子进程以root身份执行目标命令。执行记录写入`/var/log/secure`供审计 |
| 缺点 | sudoers配置语法严格，直接编辑出错可能锁死提权通道；NOPASSWD配置过多降低安全性；sudo本身是常见提权攻击目标 |

---

#### 2.1.5 SUID、SGID 与 Sticky Bit

| 维度 | 内容 |
|------|------|
| 是什么 | 三种特殊权限位，分别控制以属主身份执行、继承组、删除限制 |
| 能做什么 | SUID让普通用户以文件属主身份运行（如passwd）；SGID使目录新文件继承目录属组；Sticky Bit限制/tmp删除权限 |
| 怎么用 | `chmod u+s /usr/bin/passwd`；`chmod g+s /shared/project/`；`chmod o+t /tmp`；`chmod 4755 file` |
| 原理和工作流程 | SUID占用inode mode的setuid位，execve时将进程有效UID设为文件属主UID而非调用者，使普通用户能修改`/etc/shadow`。SGID类似，有效GID设为文件属组；作用于目录时新建文件继承目录GID。Sticky Bit作用于目录时，内核在unlink前额外校验删除者是否为文件所有者或root，否则拒绝 |
| 缺点 | SUID程序是常见提权漏洞来源，需定期扫描；误设SUID带来严重安全风险；Sticky Bit对文件已无实际意义易混淆 |

---

### 2.2 进程管理深入

本节为引导性标题，下属子节见下方五维表格。

#### 2.2.1 ps -- 查看进程快照

| 维度 | 内容 |
|------|------|
| 是什么 | 显示当前进程列表静态快照的命令 |
| 能做什么 | 列出所有进程详情；自定义输出列；按CPU内存排序；查找特定进程 |
| 怎么用 | `ps aux`；`ps -ef`；`ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -10` |
| 原理和工作流程 | ps读取`/proc`文件系统下每个数字目录（即PID）的`stat`、`status`、`cmdline`等虚拟文件，汇总进程的PID、PPID、UID、状态、CPU内存占用、命令行等信息。BSD风格`aux`与Unix风格`-ef`参数不同但都遍历`/proc`。输出为某一时刻快照，不实时刷新 |
| 缺点 | 仅快照不实时更新；`ps aux`输出列固定，自定义需记参数；进程数过多时输出冗长 |

---

#### 2.2.2 top -- 实时进程监控

| 维度 | 内容 |
|------|------|
| 是什么 | 交互式实时显示系统负载与进程资源占用的监控工具 |
| 能做什么 | 实时查看CPU内存使用率；按占用排序；查看负载均值；杀死进程；监控指定PID或用户 |
| 怎么用 | `top`；`top -p 1234`；交互按`M`按内存排序、`P`按CPU排序、`1`显示各核、`k`杀进程 |
| 原理和工作流程 | top默认每3秒读取`/proc/stat`获取CPU时间片、`/proc/meminfo`获取内存、`/proc/[pid]`获取各进程数据，计算两次采样差值得到CPU使用率。顶部区域汇总系统负载、进程总数、CPU各态占比、内存交换分区使用。下部按采样排序显示进程。交互命令通过termios捕获按键实时改变显示 |
| 缺点 | 采样间隔内瞬时高峰可能被平均稀释；交互模式下不适合脚本化，需用`-b -n 1`批处理模式；自身占用少量资源 |

---

#### 2.2.3 kill -- 发送信号控制进程

| 维度 | 内容 |
|------|------|
| 是什么 | 向进程发送控制信号的命令，用于终止、暂停、重载进程 |
| 能做什么 | 优雅终止SIGTERM；强制杀死SIGKILL；中断SIGINT；重载配置SIGHUP；按名称批量杀进程 |
| 怎么用 | `kill -15 PID`；`kill -9 PID`；`killall -15 java`；`pkill -f "spring-boot"` |
| 原理和工作流程 | kill调用`kill`系统调用，内核在目标进程的task_struct中挂起信号，下次进程从内核态返回用户态时检查并处理信号队列。SIGTERM(15)可被进程捕获，执行清理后自行退出；SIGKILL(9)由内核直接处理不可捕获忽略，立即终止进程不给清理机会。killall与pkill通过遍历`/proc`匹配进程名或命令行后批量发送信号 |
| 缺点 | 误发SIGKILL导致数据丢失与资源泄漏；信号可能被进程忽略（除SIGKILL/SIGSTOP）；向无权限进程发送信号会失败 |

---

### 2.3 网络管理深入

本节为引导性标题，下属子节见下方五维表格。

#### 2.3.1 ip -- 现代网络配置工具

| 维度 | 内容 |
|------|------|
| 是什么 | 取代ifconfig的现代网络配置与查询工具，属iproute2套件 |
| 能做什么 | 查看网卡IP与链路状态；查看路由表与ARP缓存；查询到目标的路由；查看网卡收发包统计 |
| 怎么用 | `ip addr show`；`ip route show`；`ip route get 8.8.8.8`；`ip -s link show eth0` |
| 原理和工作流程 | ip通过`netlink`套接字与内核网络子系统通信，`addr`子命令读取网卡IP地址，`link`读取链路层状态与统计，`route`读取路由表。netlink是基于socket的双向通信机制，比旧的ioctl方式效率高、信息全。`route get`由内核查询路由表返回匹配的下一跳与出接口 |
| 缺点 | 子命令与参数较多学习曲线陡；输出格式紧凑不如ifconfig直观；部分老脚本仍依赖ifconfig需兼容 |

---

#### 2.3.2 ss -- Socket 统计

| 维度 | 内容 |
|------|------|
| 是什么 | 取代netstat的Socket统计工具，直接读取内核数据结构速度快 |
| 能做什么 | 查看TCP/UDP监听端口；查看所有连接及状态；按状态过滤；汇总连接统计 |
| 怎么用 | `ss -tlnp`；`ss -tan state established`；`ss -tan state time-wait`；`ss -s` |
| 原理和工作流程 | ss通过netlink协议直接读取内核中的sock结构体与TCP状态机信息，无需像netstat那样遍历`/proc/net`。`-t`过滤TCP，`-l`只看监听，`-n`不解析服务名显示数字端口，`-p`显示占用进程。TCP连接状态反映三次握手与四次挥手过程，TIME_WAIT是主动关闭方等待2MSL的状态 |
| 缺点 | 输出信息密集新手不易解读；`-p`需root权限才能看到进程信息；部分老系统未预装iproute2 |

---

#### 2.3.3 curl -- HTTP 调试利器

| 维度 | 内容 |
|------|------|
| 是什么 | 支持多协议的命令行数据传输与HTTP调试工具 |
| 能做什么 | 发送GET/POST请求；设置请求头与请求体；下载文件；只取响应头或状态码；通过代理访问；忽略SSL校验 |
| 怎么用 | `curl -X POST http://localhost:8080/api -H "Content-Type: application/json" -d '{"name":"x"}'`；`curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/` |
| 原理和工作流程 | curl解析URL得到协议、主机、端口、路径，通过DNS解析主机IP，建立TCP连接（HTTPS再完成TLS握手），按HTTP协议构造请求行、请求头、请求体发送，接收响应后按选项处理输出。`-v`输出请求与响应头用于调试，`-o`将响应体写入文件，`-w`按格式化字符串输出传输元信息如状态码耗时 |
| 缺点 | 复杂请求参数多命令冗长；默认不跟随重定向需加`-L`；JSON请求体中的引号需转义，在Shell中易出错 |

---

#### 2.3.4 firewalld -- 防火墙管理

| 维度 | 内容 |
|------|------|
| 是什么 | CentOS/RHEL默认的动态防火墙管理工具，基于zone与service抽象规则 |
| 能做什么 | 开放关闭端口；开放服务；按来源IP配置富规则；永久与临时规则分离 |
| 怎么用 | `firewall-cmd --add-port=8080/tcp --permanent`；`firewall-cmd --reload`；`firewall-cmd --list-all` |
| 原理和工作流程 | firewalld作为daemon运行，底层操作nftables/iptables规则。采用zone概念将网络接口划分信任等级，规则绑定到zone。`--permanent`写入持久配置文件但未即时生效，`--reload`将持久配置加载到运行时。富规则支持按源地址、端口、协议精确控制，编译为底层链规则后插入netfilter钩子 |
| 缺点 | 永久与运行时配置分离易遗忘reload导致规则不生效；与底层iptables规则混用可能冲突；仅RHEL系默认，Ubuntu用ufw需另学 |

---

#### 2.3.5 SSH -- 远程连接管理

| 维度 | 内容 |
|------|------|
| 是什么 | 基于非对称加密的安全远程登录与文件传输协议及工具 |
| 能做什么 | 远程命令执行；密钥免密登录；SCP文件传输；本地与远程端口转发隧道 |
| 怎么用 | `ssh root@192.168.1.100`；`ssh-keygen -t rsa`；`scp app.jar root@host:/opt/app/`；`ssh -L 3306:localhost:3306 root@host` |
| 原理和工作流程 | SSH连接分阶段：先TCP三次握手，再协商加密算法版本，服务器发送公钥供客户端验证主机身份，随后用Diffie-Hellman协商会话密钥，之后所有通信用对称加密保护。密钥登录时客户端用私钥对挑战签名，服务器用预置公钥验证。端口转发在SSH加密通道内建立TCP隧道，将本地端口流量转发到远程 |
| 缺点 | 默认端口22易被扫描暴力破解；私钥泄露等于服务器失守；端口转发链路过长增加延迟与排查难度 |

---

### 2.4 软件包管理深入

本节为引导性标题，下属子节见下方五维表格。

#### 2.4.1 yum（RHEL/CentOS/Fedora）

| 维度 | 内容 |
|------|------|
| 是什么 | RHEL系发行版的RPM包前端管理器，处理依赖解析与仓库下载 |
| 能做什么 | 安装卸载升级软件包；搜索查询包信息；查看已装包列表；安装包组；查询文件归属 |
| 怎么用 | `yum install nginx`；`yum remove nginx`；`yum provides /usr/bin/java`；`yum groupinstall "Development Tools"` |
| 原理和工作流程 | yum读取`/etc/yum.repos.d`下仓库配置，从远程仓库下载元数据建立本地依赖关系图。安装时解析目标包依赖树，按拓扑顺序下载RPM包，调用rpm命令校验签名后安装，执行pre/post脚本。`provides`查询本地元数据中文件到包的反向映射 |
| 缺点 | 依赖解析偶有冲突需手工排除；仓库元数据缓存过期需`yum clean all`；较新版已被dnf取代但语法兼容 |

---

#### 2.4.2 apt（Debian/Ubuntu）

| 维度 | 内容 |
|------|------|
| 是什么 | Debian系的DEB包前端管理器，处理依赖解析与仓库下载 |
| 能做什么 | 安装卸载升级包；更新软件索引；搜索查询包信息；自动清理无用依赖；查找文件归属 |
| 怎么用 | `apt install nginx`；`apt update`；`apt purge nginx`；`apt autoremove`；`apt-file search /usr/bin/java` |
| 原理和工作流程 | apt读取`/etc/apt/sources.list`及`sources.list.d`的仓库地址，`update`下载Packages索引文件构建本地包数据库。安装时解析依赖调用dpkg解包DEB，执行配置脚本。`remove`保留配置文件，`purge`连配置一起删除。`autoremove`根据自动安装标记清理不再被依赖的包 |
| 缺点 | 索引需手动`apt update`刷新否则信息过期；`purge`与`remove`区别新手易混淆；apt-file需单独安装 |

---

### 2.5 系统监控深入

本节为引导性标题，下属子节见下方五维表格。

#### 2.5.1 df -- 磁盘空间监控

| 维度 | 内容 |
|------|------|
| 是什么 | 显示文件系统磁盘使用情况与可用空间的命令 |
| 能做什么 | 查看各分区容量与使用率；查看inode使用情况；显示文件系统类型 |
| 怎么用 | `df -h`；`df -i`；`df -T`；`df -h /` |
| 原理和工作流程 | df调用`statfs`系统调用读取各挂载点文件系统的超级块信息，获取总块数、已用块数、可用块数、inode总数与已用数。`-h`将块数换算为人类可读的KB/MB/GB，`-i`显示inode使用而非空间使用，`-T`额外读取文件系统类型字段 |
| 缺点 | 仅显示文件系统整体不定位大文件；网络文件系统可能因超时卡住；使用率反映含保留块，与实际可用略有出入 |

---

#### 2.5.2 free -- 内存监控

| 维度 | 内容 |
|------|------|
| 是什么 | 显示物理内存与交换分区使用情况的命令 |
| 能做什么 | 查看总内存、已用、空闲、缓存；查看交换分区使用；按固定间隔刷新 |
| 怎么用 | `free -h`；`free -h -s 2` |
| 原理和工作流程 | free读取`/proc/meminfo`获取各项内存统计。内核倾向于将空闲内存用作磁盘缓存（buff/cache），可随时回收。`used`包含进程与共享内存占用，`free`是未使用内存，`available`是扣除不可回收缓存后新进程实际可用内存。Swap使用说明物理内存不足，频繁换页性能下降 |
| 缺点 | 仅显示总量不定位具体进程内存占用；`free`小是正常现象易误判内存不足，应关注`available`；不显示内存详情需配合`/proc/meminfo` |

---

#### 2.5.3 lsof -- 查看打开的文件

| 维度 | 内容 |
|------|------|
| 是什么 | 列出系统中被进程打开的文件及网络连接的工具 |
| 能做什么 | 查端口占用进程；查进程打开的文件；查已删除未释放的文件；查目录占用进程；查网络连接 |
| 怎么用 | `lsof -i :8080`；`lsof -p 1234`；`lsof | grep deleted`；`lsof /opt/app` |
| 原理和工作流程 | lsof遍历`/proc`下各进程的`fd`目录（文件描述符表），对每个描述符读取`/proc/[pid]/fdinfo`与`/proc/[pid]/fd`的符号链接获取打开的文件路径。网络套接字通过读取`/proc/net/tcp`等映射到进程。被删除但仍被进程持有句柄的文件显示`(deleted)`标记，空间未释放 |
| 缺点 | 全量扫描`/proc`在大规模进程时较慢；需root权限才能看到其他用户进程的全部句柄；输出列多需配合grep过滤 |

---

#### 2.5.4 journalctl -- 日志管理

| 维度 | 内容 |
|------|------|
| 是什么 | systemd的统一日志查询管理工具，收集所有服务日志 |
| 能做什么 | 按服务查看日志；实时跟踪；按时间范围与级别过滤；查看内核日志与历史启动日志；清理日志 |
| 怎么用 | `journalctl -u app -f`；`journalctl -u app -n 100`；`journalctl -u app -p err`；`journalctl --vacuum-size=500M` |
| 原理和工作流程 | journald作为systemd组件收集所有服务的stdout/stderr与syslog日志，以结构化二进制格式存放在`/var/log/journal`。日志条目带时间戳、服务名、优先级等元数据，journalctl按这些字段索引过滤查询。`-f`跟踪新写入，`-p`按0-7优先级过滤，`--vacuum-size/time`按大小或时间清理旧日志释放空间 |
| 缺点 | 日志为二进制格式需journalctl查看，传统grep/awk不直接兼容；日志可能被自动轮转清理丢失历史；持久化需配置Storage=persistent |

---

#### 2.5.5 crontab -- 定时任务

| 维度 | 内容 |
|------|------|
| 是什么 | 按Cron表达式周期性执行命令或脚本的定时任务管理工具 |
| 能做什么 | 编辑查看删除定时任务；按分钟到星期五个字段定义周期；支持每用户独立任务表 |
| 怎么用 | `crontab -e`；`crontab -l`；`0 2 * * * /opt/scripts/backup-db.sh >> /var/log/backup.log 2>&1` |
| 原理和工作流程 | crond守护进程每分钟唤醒，读取`/var/spool/cron`下各用户的任务表与`/etc/crontab`，解析五字段Cron表达式（分时日月周）匹配当前时间，匹配则fork子shell执行命令。任务在最小化环境变量下运行，PATH通常只有`/usr/bin:/bin`，输出默认通过邮件发送，建议重定向到文件 |
| 缺点 | 最小粒度为1分钟无法秒级调度；环境变量精简需用绝对路径；脚本换行符为CRLF时解析失败；任务失败无重试机制 |

---

## 三、实战应用

### 3.1 JDK 多版本安装与切换

| 维度 | 内容 |
|------|------|
| 是什么 | 在同一服务器安装多个JDK版本并按需切换默认版本的实践 |
| 能做什么 | yum安装多版本OpenJDK；用alternatives切换默认java/javac；手动解压tar.gz配置环境变量 |
| 怎么用 | `yum install java-17-openjdk-devel`；`alternatives --config java`；`export JAVA_HOME=/usr/local/jdk-17` |
| 原理和工作流程 | yum将JDK安装到`/usr/lib/jvm`下各自目录。alternatives维护`/var/lib/alternatives`中的候选列表与`/etc/alternatives`下的符号链接，`java`命令实际指向`/etc/alternatives/java`再链接到选中版本的二进制。切换时仅修改符号链接目标。手动安装则通过`/etc/profile.d/jdk.sh`导出`JAVA_HOME`与`PATH`，环境变量按profile加载顺序生效 |
| 缺点 | alternatives与手动环境变量混用易冲突导致版本不一致；环境变量加载顺序复杂排查困难；多版本占用磁盘空间 |

---

### 3.2 MySQL 安装与基础配置

本节为引导性标题，下属子节见下方五维表格。

#### 3.2.1 CentOS 7 安装 MySQL 8.0

| 维度 | 内容 |
|------|------|
| 是什么 | 在CentOS 7上通过官方YUM仓库安装MySQL 8.0并完成安全初始化的流程 |
| 能做什么 | 添加官方仓库；安装服务端；启动并设开机自启；获取临时密码初始化；创建应用库与用户 |
| 怎么用 | `rpm -Uvh https://dev.mysql.com/get/mysql80-community-release-el7-11.noarch.rpm`；`yum install mysql-community-server`；`systemctl start mysqld`；`mysql_secure_installation` |
| 原理和工作流程 | rpm安装官方仓库配置文件到`/etc/yum.repos.d`，yum据此从MySQL官方源下载RPM包安装。MySQL首次启动自动生成临时密码写入`/var/log/mysqld.log`。`mysql_secure_installation`交互式引导设置新密码、移除匿名用户、禁用远程root、删除test库并刷新权限。后续用SQL语句创建业务数据库与授权用户 |
| 缺点 | 临时密码复杂易遗漏；默认密码策略强制复杂度；远程访问需额外配置防火墙与bind-address |

---

#### 3.2.2 MySQL 基础优化配置

| 维度 | 内容 |
|------|------|
| 是什么 | MySQL 8.0关键配置参数的调优实践，覆盖连接、InnoDB、慢查询 |
| 能做什么 | 设置字符集与时区；配置最大连接数与超时；调优InnoDB缓冲池与日志刷新；开启慢查询日志 |
| 怎么用 | `innodb_buffer_pool_size=2G`；`max_connections=500`；`slow_query_log=ON`；`innodb_flush_log_at_trx_commit=2` |
| 原理和工作流程 | innodb_buffer_pool缓存数据页与索引页，建议设为物理内存50%-70%以减少磁盘IO。`flush_log_at_trx_commit`控制重做日志落盘策略：0每秒刷一次性能最高但可能丢1秒数据，1每次提交都刷盘最安全性能最低，2每次提交写OS缓存每秒刷盘折中。慢查询日志记录超过long_query_time的SQL用于优化定位 |
| 缺点 | 参数需根据硬件与负载反复调优非一劳永逸；`flush_log_at_trx_commit=2`在OS崩溃时可能丢数据；缓冲池设置过大挤压系统内存 |

---

### 3.3 Redis 安装与基础配置

| 维度 | 内容 |
|------|------|
| 是什么 | 在CentOS 7上通过Remi仓库安装Redis 7.x并完成生产配置的流程 |
| 能做什么 | 启用Remi模块安装Redis 7；配置绑定地址密码与内存限制；选择内存淘汰策略；启动验证 |
| 怎么用 | `yum module enable redis:7`；`yum install redis`；`requirepass your_password`；`maxmemory-policy allkeys-lru` |
| 原理和工作流程 | Remi仓库提供较新版本Redis，yum module机制按模块流选择版本。Redis配置文件`/etc/redis.conf`中`bind`限制监听地址，`requirepass`开启密码认证，`maxmemory`限制内存上限，`maxmemory-policy`决定内存满时的淘汰算法。allkeys-lru在所有键中淘汰最近最少使用，适合通用缓存。daemonize yes使其后台运行 |
| 缺点 | 默认无密码是重大安全隐患；开放外网6379端口易被扫描入侵；内存淘汰策略选错可能导致热点数据被误删 |

---

### 3.4 Java Jar 包部署实战

本节为引导性标题，下属子节见下方五维表格。

#### 3.4.1 传统方式部署（nohup）

| 维度 | 内容 |
|------|------|
| 是什么 | 用nohup与shell脚本手动管理Java应用启停的传统部署方式 |
| 能做什么 | 后台启动jar包；用PID文件管理进程；优雅关闭超时强杀；配置JVM参数与日志输出 |
| 怎么用 | `nohup java -Xms512m -Xmx1024m -jar app.jar --spring.profiles.active=prod > app.log 2>&1 &`；`kill -15 $PID` |
| 原理和工作流程 | nohup使进程忽略SIGHUP信号，SSH断开后不退出。`&`放入后台，`$!`捕获PID写入文件。日志重定向到文件。停止时先发SIGTERM让Spring Boot优雅关闭，循环检测进程存活，超时则发SIGKILL强制终止。PID文件用于避免重复启动与定位进程 |
| 缺点 | 缺少开机自启能力需额外配置rc.local；崩溃不会自动重启需监控脚本；日志管理需手动配置轮转；无法声明服务依赖 |

---

#### 3.4.2 systemd 方式部署（推荐）

| 维度 | 内容 |
|------|------|
| 是什么 | 编写systemd service单元文件由systemd托管Java应用的部署方式 |
| 能做什么 | 声明启动停止命令与依赖；设置运行用户与工作目录；崩溃自动重启；统一日志管理；资源与安全限制 |
| 怎么用 | `systemctl start app`；`systemctl enable app`；`journalctl -u app -f` |
| 原理和工作流程 | service单元文件定义ExecStart启动命令、ExecStop停止命令、Restart重启策略。systemd按After/Wants声明依赖顺序启动，主进程退出后按Restart策略决定是否重启，RestartSec控制间隔。日志通过journald收集可用journalctl查询。NoNewPrivileges与PrivateTmp提供安全隔离。`daemon-reload`重新加载变更的单元文件 |
| 缺点 | 单元文件语法有学习成本；调试需熟悉journalctl；`Type`选择不当可能导致systemd误判服务状态 |

---

### 3.5 服务部署完整流程

| 维度 | 内容 |
|------|------|
| 是什么 | 从环境准备到日志轮转的Java应用完整部署流程 |
| 能做什么 | 安装JDK创建应用用户；部署jar包与配置；配置systemd服务；开放防火墙；启动验证；配置日志轮转 |
| 怎么用 | `useradd -m appuser`；`systemctl start app`；`firewall-cmd --add-port=8080/tcp --permanent`；`curl http://localhost:8080/actuator/health` |
| 原理和工作流程 | 流程按依赖顺序推进：先准备运行环境（JDK、专用用户、目录归属），再上传制品与配置，编写systemd单元声明启动方式与依赖，开放防火墙端口使外部可达，启动后通过健康检查接口与日志确认就绪，最后配置logrotate按日轮转压缩日志防止磁盘占满 |
| 缺点 | 步骤多易遗漏环节；手动部署效率低易出错，应向自动化交付演进；缺乏回滚机制需额外设计 |

---

## 四、常见面试题

### 面试题 1：Linux 文件权限 755、644、600 分别代表什么？如何给一个目录设置 SGID 权限并说明其作用？

| 维度 | 内容 |
|------|------|
| 是什么 | 数字权限表示法与SGID特殊权限位的考查 |
| 能做什么 | 解读755/644/600的rwx含义；用chmod设置SGID；说明SGID使目录新文件继承属组 |
| 怎么用 | `chmod 755 script.sh`；`chmod g+s /shared/project/`；`chmod 2755 /shared/project/` |
| 原理和工作流程 | 数字权限三位八进制分别对应所有者、组、其他人的rwx位之和：755为rwxr-xr-x，644为rw-r--r--，600为rw-------。SGID占用inode的setgid位，作用于目录时内核在创建文件时将新文件的GID设为目录的GID而非创建者主组，使共享目录中同组成员都能访问彼此文件 |
| 缺点 | 数字计算易出错；SGID误设可能使文件归属混乱；权限设置过宽存在安全风险 |

---

### 面试题 2：SIGTERM（15）和 SIGKILL（9）的区别？为什么推荐先发 SIGTERM？

| 维度 | 内容 |
|------|------|
| 是什么 | 两种终止进程信号在可捕获性与清理能力上的对比 |
| 能做什么 | SIGTERM允许进程捕获后清理资源；SIGKILL由内核强制终止不可捕获 |
| 怎么用 | `kill -15 PID`；等待10-30秒；`kill -9 PID` |
| 原理和工作流程 | SIGTERM是软件终止信号，内核将其挂入进程信号队列，进程从内核态返回时调用已注册的handler执行关闭连接、刷写日志、通知注册中心下线等清理后自行exit。SIGKILL不允许注册handler，内核直接回收进程资源立即终止，不执行任何清理代码，可能导致数据不完整与IPC资源泄漏 |
| 缺点 | SIGTERM可能被进程忽略导致不退出；SIGKILL造成数据丢失与资源泄漏；等待时间需根据服务特性调整 |

---

### 面试题 3：如何排查 Linux 服务器 CPU 飙高的问题？

| 维度 | 内容 |
|------|------|
| 是什么 | 定位CPU飙高根因的分层排查方法论 |
| 能做什么 | 用top定位高CPU进程；用top -H定位高CPU线程；用jstack导出线程栈定位代码行 |
| 怎么用 | `top`；`top -H -p <PID>`；`printf "%x\n" <线程PID>`；`jstack <PID> | grep -A 20 "nid=0x<十六进制>"` |
| 原理和工作流程 | 先用top观察系统整体负载与CPU使用率，按P排序找到高CPU进程PID。再用`top -H -p PID`查看该进程内各线程CPU占用，记录高占用线程的TID。Linux线程TID与进程PID在同一命名空间，将TID转十六进制后在jstack输出的`nid=0x`中匹配，定位到具体Java线程栈与代码行 |
| 缺点 | 瞬时高峰可能采样不到需多次抓取；非Java进程jstack无效需用perf或strace；多线程竞争场景定位复杂 |

---

### 面试题 4：Linux 中如何查找被占用的端口？TIME_WAIT 状态过多怎么办？

| 维度 | 内容 |
|------|------|
| 是什么 | 端口占用排查与TCP TIME_WAIT堆积的解决方案 |
| 能做什么 | 用ss/lsof/netstat查端口占用；启用tcp_tw_reuse复用TIME_WAIT；调整超时与上限；使用长连接 |
| 怎么用 | `ss -tlnp | grep 8080`；`lsof -i :8080`；`sysctl -w net.ipv4.tcp_tw_reuse=1` |
| 原理和工作流程 | ss与lsof读取内核socket表查找监听指定端口的进程。TIME_WAIT是主动关闭方发送最后ACK后等待2MSL的状态，使延迟报文失效。高并发短连接场景大量TIME_WAIT占用端口资源。`tcp_tw_reuse=1`允许新连接复用TIME_WAIT的端口（需配合tcp_timestamps防歧义），`tcp_max_tw_buckets`限制总量，长连接减少连接创建关闭频率 |
| 缺点 | tcp_tw_reuse仅对出站连接有效；降低超时可能在NAT环境下引发报文混淆；调整内核参数需评估网络环境 |

---

### 面试题 5：systemd 相比传统 init 有什么优势？如何编写一个 systemd service 文件？

| 维度 | 内容 |
|------|------|
| 是什么 | systemd相比SysV init的架构优势与service单元文件编写 |
| 能做什么 | 并行启动服务；声明依赖；崩溃自动重启；统一日志；cgroups资源限制 |
| 怎么用 | `[Unit]`/`[Service]`/`[Install]`三段式；`ExecStart=`；`Restart=on-failure`；`WantedBy=multi-user.target` |
| 原理和工作流程 | SysV init按脚本编号串行启动，systemd读取单元文件构建依赖图，无依赖的服务并行启动缩短开机时间。`After`声明启动顺序，`Requires`强依赖，`Wants`弱依赖。`Restart`策略使进程崩溃自动重启，`RestartSec`控制间隔。日志统一由journald收集。cgroups限制CPU内存等资源 |
| 缺点 | 单元文件字段多需查阅文档；依赖声明错误可能导致启动异常；并行启动顺序不确定需显式声明 |

---

## 五、避坑指南

本节为辅助内容，无五维表格。

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./02-Linux系统管理与服务部署.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
