// 通用 HTTP 工具：统一响应格式、JWT 解析、文件上传、Markdown TOC 生成
//
// 依赖（均为可选，按需安装）：
//   jsonwebtoken、md5、multer、markdown-toc
// 注意：JWT 密钥一律从 process.env.JWT_SECRET 读取，不要硬编码。
//
// 用法：
//   const tool = require("./http-tool");
//   res.json(tool.success("ok", data));
//   const upload = tool.createUploader({ dest: "/tmp/uploads" });
//   router.post("/file", upload.single("file"), handler);

const jwt = require("jsonwebtoken");
const md5 = require("md5");
const multer = require("multer");
const path = require("path");
const toc = require("markdown-toc");

const SUCCESS_CODE = 200;

// 统一响应结构
function formatResponse(code, msg, data) {
  return { code, msg, data };
}

// 成功响应便捷方法
function success(msg = "success", data = null) {
  return formatResponse(SUCCESS_CODE, msg, data);
}

// 解析 Bearer Token（密钥来自环境变量）
function analysisToken(token) {
  try {
    return jwt.verify(token.split(" ")[1], md5(process.env.JWT_SECRET));
  } catch (error) {
    const err = new Error("Token验证失败");
    err.code = 403;
    throw err;
  }
}

// 将 Sequelize 结果数组提取 dataValues
function handleDataPattern(data) {
  return data.map((i) => i.dataValues);
}

// 创建文件上传器（目标目录可配置，避免硬编码项目路径）
function createUploader({ dest, maxSize = 2_000_000, maxFiles = 1 } = {}) {
  const storage = multer.diskStorage({
    destination: function (req, file, cb) {
      // 优先使用传入 dest，其次环境变量 UPLOAD_DIR，最后回退到 cwd 下默认目录
      cb(null, dest || process.env.UPLOAD_DIR || path.join(process.cwd(), "public/static/uploads"));
    },
    filename: function (req, file, cb) {
      const basename = path.basename(file.originalname, path.extname(file.originalname));
      const extname = path.extname(file.originalname);
      const newName = basename + Date.now() + Math.floor(Math.random() * 9000 + 1000) + extname;
      cb(null, newName);
    },
  });
  return multer({
    storage,
    limits: { fileSize: maxSize, files: maxFiles },
  });
}

// 将 Markdown 的扁平 TOC 转为带层级的树结构，并为标题注入 anchor id
function handleTOC(info) {
  const flat = toc(info.markdownContent).json;

  function createTOCItem(item) {
    return { name: item.content, anchor: item.slug, level: item.lvl, children: [] };
  }

  function transfer(flatArr) {
    const stack = [];
    const result = [];
    function handleItem(item) {
      const top = stack[stack.length - 1];
      if (!top) {
        stack.push(item);
      } else if (item.level > top.level) {
        top.children.push(item);
        stack.push(item);
      } else {
        stack.pop();
        handleItem(item);
      }
    }
    let min = 6;
    for (const i of flatArr) if (i.lvl < min) min = i.lvl;
    for (const item of flatArr) {
      const tocItem = createTOCItem(item);
      if (tocItem.level === min) result.push(tocItem);
      handleItem(tocItem);
    }
    return result;
  }

  info.toc = transfer(flat);
  delete info.markdownContent;

  const tagMap = { 1: "h1", 2: "h2", 3: "h3", 4: "h4", 5: "h5", 6: "h6" };
  for (const i of info.toc) {
    const tag = tagMap[i.lvl];
    if (tag) {
      const newStr = `<${tag} id="${i.slug}">`;
      info.htmlContent = info.htmlContent.replace(`<${tag}>`, newStr);
    }
  }
  return info;
}

module.exports = {
  SUCCESS_CODE,
  formatResponse,
  success,
  analysisToken,
  handleDataPattern,
  createUploader,
  handleTOC,
};
