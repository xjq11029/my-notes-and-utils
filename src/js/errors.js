// 通用自定义错误类层次（与具体业务无关，可跨项目复用）
//
// 依赖：无第三方依赖。
// 用法：
//   const { ServiceError, UnauthorizedError } = require("./errors");
//   throw new UnauthorizedError("登录已过期");
//   在统一错误处理中间件中调用 err.toResponseJSON() 生成响应体。

const { formatResponse } = require("./http-tool");

/**
 * 错误基类：携带业务状态码 code
 */
class ServiceError extends Error {
  /**
   * @param {string} message 错误消息
   * @param {number} code    业务状态码
   */
  constructor(message, code) {
    super(message);
    this.code = code;
  }

  // 格式化为统一响应结构
  toResponseJSON() {
    return formatResponse(this.code, this.message, null);
  }
}

// 文件上传错误（413）
exports.UploadError = class extends ServiceError {
  constructor(message) {
    super(message, 413);
  }
};

// 未认证（401）
exports.UnauthorizedError = class extends ServiceError {
  constructor(message) {
    super(message, 401);
  }
};

// 禁止访问（403）
exports.ForbiddenError = class extends ServiceError {
  constructor(message) {
    super(message, 403);
  }
};

// 参数校验失败（406）
exports.ValidationError = class extends ServiceError {
  constructor(message) {
    super(message, 406);
  }
};

// 资源不存在（406）
exports.NotFoundError = class extends ServiceError {
  constructor() {
    super("not found", 406);
  }
};

// 未知/服务器内部错误（500）
exports.UnknownError = class extends ServiceError {
  constructor() {
    super("server internal error", 500);
  }
};

module.exports.ServiceError = ServiceError;
