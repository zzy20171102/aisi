# 人力资源管理系统 四视图追踪矩阵

> 生成时间：2026-08-23T20:38:56 ｜ 边总数：170

## 追踪概览

- 需求 67 条 ｜ 模块 32 个 ｜ 架构层 4 层
- 追踪边 170 条
- 孤儿需求（无模块承载）：0
- 空模块（无承载需求）：0
- 未分层模块：8（MOD-00, MOD-01, MOD-02, MOD-03, MOD-05, MOD-06, MOD-08, MOD-09）
- 空架构层：0

## 需求 → 模块（satisfy）

| 需求 | 模块 |
|---|---|
| REQ-001 功能需求 | MOD-00 |
| REQ-001.1 员工资料管理 | MOD-01 |
| REQ-001.1.1 基本资料管理 | MOD-11 |
| REQ-001.1.1.1 档案增删改查 | MOD-11 |
| REQ-001.1.1.2 工号自动生成 | MOD-11 |
| REQ-001.1.1.3 必填项校验 | MOD-11 |
| REQ-001.1.1.4 多条件搜索 | MOD-11 |
| REQ-001.1.2 高级资料查询 | MOD-12 |
| REQ-001.1.2.1 培训资料查询 | MOD-12 |
| REQ-001.1.2.2 考评资料查询 | MOD-12 |
| REQ-001.1.2.3 工资信息查询 | MOD-12 |
| REQ-001.2 员工奖惩管理 | MOD-02 |
| REQ-001.2.1 添加奖惩 | MOD-21 |
| REQ-001.2.2 奖惩管理列表 | MOD-22 |
| REQ-001.3 员工培训与考评 | MOD-03 |
| REQ-001.3.1 培训管理 | MOD-31 |
| REQ-001.3.1.1 批量添加培训 | MOD-31 |
| REQ-001.3.1.2 在训唯一约束 | MOD-31 |
| REQ-001.3.1.3 培训进度管理 | MOD-31 |
| REQ-001.3.2 考评管理 | MOD-32 |
| REQ-001.3.2.1 批量添加考评 | MOD-32 |
| REQ-001.4 员工调动管理 | MOD-04 |
| REQ-001.5 薪资管理 | MOD-05 |
| REQ-001.5.1 工资账套管理 | MOD-51 |
| REQ-001.5.2 员工账套设置 | MOD-52 |
| REQ-001.5.3 工资表管理 | MOD-53 |
| REQ-001.6 统计分析 | MOD-06 |
| REQ-001.6.1 员工积分统计 | MOD-61 |
| REQ-001.6.2 人事信息分析 | MOD-62 |
| REQ-001.6.3 人事记录分析 | MOD-63 |
| REQ-001.7 人事通讯 | MOD-07 |
| REQ-001.8 基础信息设置 | MOD-08 |
| REQ-001.8.1 部门管理 | MOD-81 |
| REQ-001.8.2 职位管理 | MOD-82 |
| REQ-001.8.3 职称管理 | MOD-83 |
| REQ-001.8.4 奖惩规则管理 | MOD-84 |
| REQ-001.8.5 权限组管理 | MOD-85 |
| REQ-001.9 系统管理 | MOD-09 |
| REQ-001.9.1 操作员管理 | MOD-91 |
| REQ-001.9.2 菜单权限配置 | MOD-92 |
| REQ-002 性能需求 | MOD-00 |
| REQ-002.1 操作响应性能 | MOD-00 |
| REQ-002.2 低配运行能力 | MOD-00 |
| REQ-003 数据需求 | MOD-20 |
| REQ-003.1 员工主数据 | MOD-20 |
| REQ-003.2 权限数据模型 | MOD-20 |
| REQ-003.3 培训与考评数据 | MOD-20 |
| REQ-003.4 薪资数据 | MOD-20 |
| REQ-003.5 奖惩与积分数据 | MOD-20 |
| REQ-003.6 统计维度数据 | MOD-20 |
| REQ-003.7 基础信息数据 | MOD-20 |
| REQ-003.8 数据交换格式 | MOD-20 |
| REQ-004 部署需求 | MOD-00 |
| REQ-004.1 部署形态 | MOD-00 |
| REQ-004.2 服务器运行环境 | MOD-00 |
| REQ-004.3 安装包大小 | MOD-00 |
| REQ-004.4 客户端浏览器环境 | MOD-00 |
| REQ-004.5 数据库环境 | MOD-00 |
| REQ-005 安全需求 | MOD-10 |
| REQ-005.1 身份验证 | MOD-10 |
| REQ-005.2 RBAC鉴权 | MOD-10 |
| REQ-005.3 操作审计日志 | MOD-10 |
| REQ-005.4 保密级别授权 | MOD-10 |
| REQ-006 接口需求 | MOD-40 |
| REQ-006.1 前后端数据接口 | MOD-40 |
| REQ-006.2 在线讯息接口 | MOD-40 |
| REQ-006.3 数据导入导出接口 | MOD-40 |

## 模块 → 架构层（allocate）

| 模块 | 架构层 |
|---|---|
| MOD-00 人力资源管理系统 | ⚠ 无 |
| MOD-01 员工资料管理子系统 | ⚠ 无 |
| MOD-11 基本资料管理模块 | LAY-01 |
| MOD-12 高级资料查询模块 | LAY-01 |
| MOD-02 员工奖惩管理子系统 | ⚠ 无 |
| MOD-21 添加奖惩模块 | LAY-01 |
| MOD-22 奖惩管理列表模块 | LAY-01 |
| MOD-03 员工培训与考评子系统 | ⚠ 无 |
| MOD-31 培训管理模块 | LAY-01 |
| MOD-32 考评管理模块 | LAY-01 |
| MOD-04 员工调动管理模块 | LAY-01 |
| MOD-05 薪资管理子系统 | ⚠ 无 |
| MOD-51 工资账套管理模块 | LAY-01 |
| MOD-52 员工账套设置模块 | LAY-01 |
| MOD-53 工资表管理模块 | LAY-01 |
| MOD-06 统计分析子系统 | ⚠ 无 |
| MOD-61 员工积分统计模块 | LAY-01 |
| MOD-62 人事信息分析模块 | LAY-01 |
| MOD-63 人事记录分析模块 | LAY-01 |
| MOD-07 人事通讯模块 | LAY-01 |
| MOD-08 基础信息设置子系统 | ⚠ 无 |
| MOD-81 部门管理模块 | LAY-01 |
| MOD-82 职位管理模块 | LAY-01 |
| MOD-83 职称管理模块 | LAY-01 |
| MOD-84 奖惩规则管理模块 | LAY-01 |
| MOD-85 权限组管理模块 | LAY-01 |
| MOD-09 系统管理子系统 | ⚠ 无 |
| MOD-91 操作员管理模块 | LAY-01 |
| MOD-92 菜单权限配置模块 | LAY-01 |
| MOD-10 RBAC 安全服务 | LAY-03 |
| MOD-20 数据持久层 | LAY-04 |
| MOD-40 前后端交互服务 | LAY-02 |

## 流程步骤 → 模块（executes）

| 流程步骤 | 模块 |
|---|---|
| PRC-001.S01 输入用户名密码提交登录表单 | MOD-92 |
| PRC-001.S02 自定义验证与表单验证 | MOD-10 |
| PRC-001.S03 身份验证通过后获取当前用户的所有角色 | MOD-10 |
| PRC-001.S04 根据角色加载对应的权限菜单（默认不加载无权限菜单 | MOD-92 |
| PRC-001.S05 发起业务操作或直接输入 URL 访问 | MOD-11 |
| PRC-001.S06 请求路径分析与 Spring Security  | MOD-10 |
| PRC-001.S07 放行响应资源并记录操作日志 | MOD-10 |
| PRC-002.S01 在基本资料管理录入员工信息 | MOD-11 |
| PRC-002.S02 必填项校验（工号以外全部必填） | MOD-11 |
| PRC-002.S03 数据库自动生成员工工号 | MOD-20 |
| PRC-002.S04 保存员工基本档案 | MOD-20 |
| PRC-002.S05 维护高级资料（培训/考评/工资信息） | MOD-12 |
| PRC-003.S01 在奖惩管理中选择员工（穿梭框/tab） | MOD-21 |
| PRC-003.S02 填写奖惩记录并保存（同一员工可多条 1:N） | MOD-21 |
| PRC-003.S03 持久化奖惩记录 | MOD-20 |
| PRC-003.S04 按奖惩规则自动累计员工积分 | MOD-61 |
| PRC-003.S05 在奖惩管理列表查看有奖惩信息的员工与详情 | MOD-22 |
| PRC-004.S01 批量添加员工培训 | MOD-31 |
| PRC-004.S02 在训唯一约束校验（同一员工同期仅一个培训） | MOD-31 |
| PRC-004.S03 保存培训记录并展示进度条 | MOD-31 |
| PRC-004.S04 更新培训进度 | MOD-31 |
| PRC-004.S05 培训完成后删除当前培训记录（方可添加新培训） | MOD-31 |
| PRC-005.S01 批量添加员工评价（评分条/步骤条界面） | MOD-32 |
| PRC-005.S02 一对一关系校验（员工与考评 1:1） | MOD-32 |
| PRC-005.S03 保存考评结果（考评日期/内容/结果） | MOD-20 |
| PRC-006.S01 选择员工并填写调动信息（table 内嵌 tab | MOD-04 |
| PRC-006.S02 保存调动记录（员工与调动 1:N） | MOD-20 |
| PRC-007.S01 维护工资账套各项（奖金/基本工资/提成） | MOD-51 |
| PRC-007.S02 设置当前套账 | MOD-51 |
| PRC-007.S03 为员工设置工资账套 | MOD-52 |
| PRC-007.S04 工资表查询与筛选（按职称/部门），查看套账详情 | MOD-53 |
| PRC-008.S01 用户操作触发前端请求 | MOD-92 |
| PRC-008.S02 前端拦截器统一拦截所有请求 | MOD-40 |
| PRC-008.S03 后端返回数据或消息，前端分析需要返回数据还是消息 | MOD-40 |

## 全部追踪边

| 源 | 关系 | 目标 | 证据 |
|---|---|---|---|
| REQ-001 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-002 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-002.1 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-002.2 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-004 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-004.1 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-004.2 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-004.3 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-004.4 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-004.5 | 实现 | MOD-00 | MOD-00.requirements |
| REQ-001.1 | 实现 | MOD-01 | MOD-01.requirements |
| REQ-001.1.1 | 实现 | MOD-11 | MOD-11.requirements |
| REQ-001.1.1.1 | 实现 | MOD-11 | MOD-11.requirements |
| REQ-001.1.1.2 | 实现 | MOD-11 | MOD-11.requirements |
| REQ-001.1.1.3 | 实现 | MOD-11 | MOD-11.requirements |
| REQ-001.1.1.4 | 实现 | MOD-11 | MOD-11.requirements |
| MOD-11 | 部署于 | LAY-01 | MOD-11.layer |
| REQ-001.1.2 | 实现 | MOD-12 | MOD-12.requirements |
| REQ-001.1.2.1 | 实现 | MOD-12 | MOD-12.requirements |
| REQ-001.1.2.2 | 实现 | MOD-12 | MOD-12.requirements |
| REQ-001.1.2.3 | 实现 | MOD-12 | MOD-12.requirements |
| MOD-12 | 部署于 | LAY-01 | MOD-12.layer |
| REQ-001.2 | 实现 | MOD-02 | MOD-02.requirements |
| REQ-001.2.1 | 实现 | MOD-21 | MOD-21.requirements |
| MOD-21 | 部署于 | LAY-01 | MOD-21.layer |
| REQ-001.2.2 | 实现 | MOD-22 | MOD-22.requirements |
| MOD-22 | 部署于 | LAY-01 | MOD-22.layer |
| REQ-001.3 | 实现 | MOD-03 | MOD-03.requirements |
| REQ-001.3.1 | 实现 | MOD-31 | MOD-31.requirements |
| REQ-001.3.1.1 | 实现 | MOD-31 | MOD-31.requirements |
| REQ-001.3.1.2 | 实现 | MOD-31 | MOD-31.requirements |
| REQ-001.3.1.3 | 实现 | MOD-31 | MOD-31.requirements |
| MOD-31 | 部署于 | LAY-01 | MOD-31.layer |
| REQ-001.3.2 | 实现 | MOD-32 | MOD-32.requirements |
| REQ-001.3.2.1 | 实现 | MOD-32 | MOD-32.requirements |
| MOD-32 | 部署于 | LAY-01 | MOD-32.layer |
| REQ-001.4 | 实现 | MOD-04 | MOD-04.requirements |
| MOD-04 | 部署于 | LAY-01 | MOD-04.layer |
| REQ-001.5 | 实现 | MOD-05 | MOD-05.requirements |
| REQ-001.5.1 | 实现 | MOD-51 | MOD-51.requirements |
| MOD-51 | 部署于 | LAY-01 | MOD-51.layer |
| REQ-001.5.2 | 实现 | MOD-52 | MOD-52.requirements |
| MOD-52 | 部署于 | LAY-01 | MOD-52.layer |
| REQ-001.5.3 | 实现 | MOD-53 | MOD-53.requirements |
| MOD-53 | 部署于 | LAY-01 | MOD-53.layer |
| REQ-001.6 | 实现 | MOD-06 | MOD-06.requirements |
| REQ-001.6.1 | 实现 | MOD-61 | MOD-61.requirements |
| MOD-61 | 部署于 | LAY-01 | MOD-61.layer |
| REQ-001.6.2 | 实现 | MOD-62 | MOD-62.requirements |
| MOD-62 | 部署于 | LAY-01 | MOD-62.layer |
| REQ-001.6.3 | 实现 | MOD-63 | MOD-63.requirements |
| MOD-63 | 部署于 | LAY-01 | MOD-63.layer |
| REQ-001.7 | 实现 | MOD-07 | MOD-07.requirements |
| MOD-07 | 部署于 | LAY-01 | MOD-07.layer |
| REQ-001.8 | 实现 | MOD-08 | MOD-08.requirements |
| REQ-001.8.1 | 实现 | MOD-81 | MOD-81.requirements |
| MOD-81 | 部署于 | LAY-01 | MOD-81.layer |
| REQ-001.8.2 | 实现 | MOD-82 | MOD-82.requirements |
| MOD-82 | 部署于 | LAY-01 | MOD-82.layer |
| REQ-001.8.3 | 实现 | MOD-83 | MOD-83.requirements |
| MOD-83 | 部署于 | LAY-01 | MOD-83.layer |
| REQ-001.8.4 | 实现 | MOD-84 | MOD-84.requirements |
| MOD-84 | 部署于 | LAY-01 | MOD-84.layer |
| REQ-001.8.5 | 实现 | MOD-85 | MOD-85.requirements |
| MOD-85 | 部署于 | LAY-01 | MOD-85.layer |
| REQ-001.9 | 实现 | MOD-09 | MOD-09.requirements |
| REQ-001.9.1 | 实现 | MOD-91 | MOD-91.requirements |
| MOD-91 | 部署于 | LAY-01 | MOD-91.layer |
| REQ-001.9.2 | 实现 | MOD-92 | MOD-92.requirements |
| MOD-92 | 部署于 | LAY-01 | MOD-92.layer |
| REQ-005 | 实现 | MOD-10 | MOD-10.requirements |
| REQ-005.1 | 实现 | MOD-10 | MOD-10.requirements |
| REQ-005.2 | 实现 | MOD-10 | MOD-10.requirements |
| REQ-005.3 | 实现 | MOD-10 | MOD-10.requirements |
| REQ-005.4 | 实现 | MOD-10 | MOD-10.requirements |
| MOD-10 | 部署于 | LAY-03 | MOD-10.layer |
| REQ-003 | 实现 | MOD-20 | MOD-20.requirements |
| REQ-003.1 | 实现 | MOD-20 | MOD-20.requirements |
| REQ-003.2 | 实现 | MOD-20 | MOD-20.requirements |
| REQ-003.3 | 实现 | MOD-20 | MOD-20.requirements |
| REQ-003.4 | 实现 | MOD-20 | MOD-20.requirements |
| REQ-003.5 | 实现 | MOD-20 | MOD-20.requirements |
| REQ-003.6 | 实现 | MOD-20 | MOD-20.requirements |
| REQ-003.7 | 实现 | MOD-20 | MOD-20.requirements |
| REQ-003.8 | 实现 | MOD-20 | MOD-20.requirements |
| MOD-20 | 部署于 | LAY-04 | MOD-20.layer |
| REQ-006 | 实现 | MOD-40 | MOD-40.requirements |
| REQ-006.1 | 实现 | MOD-40 | MOD-40.requirements |
| REQ-006.2 | 实现 | MOD-40 | MOD-40.requirements |
| REQ-006.3 | 实现 | MOD-40 | MOD-40.requirements |
| MOD-40 | 部署于 | LAY-02 | MOD-40.layer |
| MOD-11 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-12 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-21 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-22 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-31 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-32 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-04 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-51 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-52 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-53 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-61 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-62 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-63 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-07 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-81 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-82 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-83 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-84 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-85 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-91 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-92 | 部署于 | LAY-01 | LAY-01.modules |
| MOD-40 | 部署于 | LAY-02 | LAY-02.modules |
| MOD-10 | 部署于 | LAY-03 | LAY-03.modules |
| MOD-20 | 部署于 | LAY-04 | LAY-04.modules |
| SVC-01 | 连接 | MOD-10 | SVC-01.module |
| SVC-02 | 连接 | MOD-40 | SVC-02.module |
| SVC-03 | 连接 | MOD-40 | SVC-03.module |
| SVC-04 | 连接 | MOD-06 | SVC-04.module |
| SVC-05 | 连接 | MOD-20 | SVC-05.module |
| PRC-001.S01 | 执行 | MOD-92 | PRC-001 步骤执行模块 |
| PRC-001.S02 | 执行 | MOD-10 | PRC-001 步骤执行模块 |
| PRC-001.S03 | 执行 | MOD-10 | PRC-001 步骤执行模块 |
| PRC-001.S04 | 执行 | MOD-92 | PRC-001 步骤执行模块 |
| PRC-001.S05 | 执行 | MOD-11 | PRC-001 步骤执行模块 |
| PRC-001.S06 | 执行 | MOD-10 | PRC-001 步骤执行模块 |
| PRC-001.S07 | 执行 | MOD-10 | PRC-001 步骤执行模块 |
| PRC-002.S01 | 执行 | MOD-11 | PRC-002 步骤执行模块 |
| PRC-002.S02 | 执行 | MOD-11 | PRC-002 步骤执行模块 |
| PRC-002.S03 | 执行 | MOD-20 | PRC-002 步骤执行模块 |
| PRC-002.S04 | 执行 | MOD-20 | PRC-002 步骤执行模块 |
| PRC-002.S05 | 执行 | MOD-12 | PRC-002 步骤执行模块 |
| PRC-003.S01 | 执行 | MOD-21 | PRC-003 步骤执行模块 |
| PRC-003.S02 | 执行 | MOD-21 | PRC-003 步骤执行模块 |
| PRC-003.S03 | 执行 | MOD-20 | PRC-003 步骤执行模块 |
| PRC-003.S04 | 执行 | MOD-61 | PRC-003 步骤执行模块 |
| PRC-003.S05 | 执行 | MOD-22 | PRC-003 步骤执行模块 |
| PRC-004.S01 | 执行 | MOD-31 | PRC-004 步骤执行模块 |
| PRC-004.S02 | 执行 | MOD-31 | PRC-004 步骤执行模块 |
| PRC-004.S03 | 执行 | MOD-31 | PRC-004 步骤执行模块 |
| PRC-004.S04 | 执行 | MOD-31 | PRC-004 步骤执行模块 |
| PRC-004.S05 | 执行 | MOD-31 | PRC-004 步骤执行模块 |
| PRC-005.S01 | 执行 | MOD-32 | PRC-005 步骤执行模块 |
| PRC-005.S02 | 执行 | MOD-32 | PRC-005 步骤执行模块 |
| PRC-005.S03 | 执行 | MOD-20 | PRC-005 步骤执行模块 |
| PRC-006.S01 | 执行 | MOD-04 | PRC-006 步骤执行模块 |
| PRC-006.S02 | 执行 | MOD-20 | PRC-006 步骤执行模块 |
| PRC-007.S01 | 执行 | MOD-51 | PRC-007 步骤执行模块 |
| PRC-007.S02 | 执行 | MOD-51 | PRC-007 步骤执行模块 |
| PRC-007.S03 | 执行 | MOD-52 | PRC-007 步骤执行模块 |
| PRC-007.S04 | 执行 | MOD-53 | PRC-007 步骤执行模块 |
| PRC-008.S01 | 执行 | MOD-92 | PRC-008 步骤执行模块 |
| PRC-008.S02 | 执行 | MOD-40 | PRC-008 步骤执行模块 |
| PRC-008.S03 | 执行 | MOD-40 | PRC-008 步骤执行模块 |
| MOD-21 | 连接 | MOD-20 | DF-01:奖惩记录 |
| MOD-20 | 连接 | MOD-61 | DF-02:奖惩积分数据 |
| MOD-51 | 连接 | MOD-20 | DF-03:工资账套定义与当前套账 |
| MOD-20 | 连接 | MOD-53 | DF-04:工资表数据（按职称/部门筛选） |
| MOD-20 | 连接 | MOD-62 | DF-05:人事维度分布数据（7 维） |
| MOD-11 | 连接 | MOD-12 | DF-06:员工档案与高级资料关联 |
| MOD-10 | 连接 | MOD-92 | IF-01:登录认证接口 |
| MOD-40 | 连接 | MOD-07 | IF-02:在线讯息接口 |
| MOD-40 | 连接 | MOD-11 | IF-03:Excel 导入导出接口 |
| MOD-40 | 连接 | MOD-11 | IF-04:业务数据接口 |
| MOD-40 | 连接 | MOD-21 | IF-04:业务数据接口 |
| MOD-40 | 连接 | MOD-31 | IF-04:业务数据接口 |
| MOD-40 | 连接 | MOD-51 | IF-04:业务数据接口 |
| MOD-40 | 连接 | MOD-53 | IF-04:业务数据接口 |
| MOD-40 | 连接 | MOD-61 | IF-04:业务数据接口 |
| MOD-40 | 连接 | MOD-62 | IF-04:业务数据接口 |
