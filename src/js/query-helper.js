// 通用 Sequelize 查询工具：统一处理分页、模糊搜索、时间范围筛选
//
// 依赖：sequelize（仅用到 Op）。
// 用法：
//   const { paginate, buildWhere } = require("./query-helper");
//   const result = await paginate(ArticleModel, req.query, {
//     fuzzy: ["title"],
//     range: ["createdAt"],
//   });

const { Op } = require("sequelize");

/**
 * 构建 where 条件
 * @param {Object} query          已剔除 pageNum/pageSize 的查询参数
 * @param {Object} [opts]
 * @param {string[]} [opts.fuzzy] 模糊搜索字段（Op.like）
 * @param {string[]} [opts.range] 数组式时间范围字段（Op.between）
 * @returns {Object} Sequelize where 条件对象
 */
function buildWhere(query, { fuzzy = [], range = [] } = {}) {
  const where = {};
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || value === "") continue;
    if (fuzzy.includes(key)) {
      where[key] = { [Op.like]: `%${value}%` };
    } else if (range.includes(key)) {
      if (Array.isArray(value) && value.length === 2) {
        where[key] = { [Op.between]: value };
      }
    } else {
      where[key] = value;
    }
  }
  return where;
}

/**
 * 统一分页查询
 * @param {Object} model          Sequelize 模型
 * @param {Object} params         含 pageNum/pageSize 及筛选条件的参数
 * @param {Object} [opts]
 * @param {string[]} [opts.fuzzy] 模糊搜索字段
 * @param {string[]} [opts.range] 时间范围字段
 * @param {string}  [opts.orderField] 排序字段，默认 createTime
 * @returns {Promise<{data:Array,total:number,pageNum:number,pageSize:number}>}
 */
async function paginate(model, params, { fuzzy = [], range = [], orderField = "createTime" } = {}) {
  const { pageNum = 1, pageSize = 10, ...query } = params;
  const where = buildWhere(query, { fuzzy, range });
  const offset = (Number(pageNum) - 1) * Number(pageSize);
  const { count, rows } = await model.findAndCountAll({
    where,
    offset,
    limit: Number(pageSize),
    order: [[orderField, "DESC"]],
  });
  return {
    data: rows,
    total: count,
    pageNum: Number(pageNum),
    pageSize: Number(pageSize),
  };
}

module.exports = { buildWhere, paginate };
