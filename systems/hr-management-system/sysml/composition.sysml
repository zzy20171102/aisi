package HrManagementSystemComposition {
    part def Mod00 {
        doc /* MOD-00 人力资源管理系统（subsystem）：系统级功能、性能与部署目标承载；端到端人事业务闭环 */
        // B/S 架构整体；六大功能模块对应人事工作基本流程（样例报告 §二）；系统级需求（性能/部署）由整体承载
        part mod01: Mod01;  // 员工资料管理子系统
        part mod02: Mod02;  // 员工奖惩管理子系统
        part mod03: Mod03;  // 员工培训与考评子系统
        part mod04: Mod04;  // 员工调动管理模块
        part mod05: Mod05;  // 薪资管理子系统
        part mod06: Mod06;  // 统计分析子系统
        part mod07: Mod07;  // 人事通讯模块
        part mod08: Mod08;  // 基础信息设置子系统
        part mod09: Mod09;  // 系统管理子系统
        part mod10: Mod10;  // RBAC 安全服务
        part mod20: Mod20;  // 数据持久层
        part mod40: Mod40;  // 前后端交互服务
    }
    part def Mod01 {
        doc /* MOD-01 员工资料管理子系统（subsystem）：员工基本资料与高级资料管理 */
        part mod11: Mod11;  // 基本资料管理模块
        part mod12: Mod12;  // 高级资料查询模块
    }
    part def Mod11 {
        doc /* MOD-11 基本资料管理模块（module）：档案增删改查（按id更新）；工号自动生成；必填项校验；多条件搜索 */
        // 员工实体与奖惩 1:N、与调动 1:N、与在训 1:1、与考评 1:1（样例报告 §4/§5/§6）
    }
    part def Mod12 {
        doc /* MOD-12 高级资料查询模块（module）：培训资料查询；考评资料查询；工资信息查询 */
        // 高级资料 = 培训 + 考评 + 工资三部分（样例报告 §4.3.2）
    }
    part def Mod02 {
        doc /* MOD-02 员工奖惩管理子系统（subsystem）：奖惩记录全生命周期管理 */
        // 员工与奖惩信息一对多
        part mod21: Mod21;  // 添加奖惩模块
        part mod22: Mod22;  // 奖惩管理列表模块
    }
    part def Mod21 {
        doc /* MOD-21 添加奖惩模块（module）：为员工添加奖惩记录，同一员工可多条 */
        // UI 使用穿梭框与 tab 标签
    }
    part def Mod22 {
        doc /* MOD-22 奖惩管理列表模块（module）：展示有奖惩信息的全部员工；查看奖惩详情 */
    }
    part def Mod03 {
        doc /* MOD-03 员工培训与考评子系统（subsystem）：培训业务与评价业务管理 */
        part mod31: Mod31;  // 培训管理模块
        part mod32: Mod32;  // 考评管理模块
    }
    part def Mod31 {
        doc /* MOD-31 培训管理模块（module）：批量添加培训；在训唯一约束（同期仅1个）；培训进度维护（进度条） */
        // 培训完成删除当前培训后方可添加新培训
    }
    part def Mod32 {
        doc /* MOD-32 考评管理模块（module）：批量添加评价（评分条/步骤条）；考评增删改查 */
        // 员工与考评一对一
    }
    part def Mod04 {
        doc /* MOD-04 员工调动管理模块（module）：调动信息增删改查 */
        // 员工与调动一对多；UI 为 table 内嵌 table
    }
    part def Mod05 {
        doc /* MOD-05 薪资管理子系统（subsystem）：工资账套、员工账套、工资表管理 */
        part mod51: Mod51;  // 工资账套管理模块
        part mod52: Mod52;  // 员工账套设置模块
        part mod53: Mod53;  // 工资表管理模块
    }
    part def Mod51 {
        doc /* MOD-51 工资账套管理模块（module）：奖金/基本工资/提成各项增删改查；设置当前套账 */
    }
    part def Mod52 {
        doc /* MOD-52 员工账套设置模块（module）：为员工设置工资账套 */
    }
    part def Mod53 {
        doc /* MOD-53 工资表管理模块（module）：工资搜索查看；按职称/部门表内筛选；套账详情查看 */
    }
    part def Mod06 {
        doc /* MOD-06 统计分析子系统（subsystem）：积分统计与人事分析 */
        part mod61: Mod61;  // 员工积分统计模块
        part mod62: Mod62;  // 人事信息分析模块
        part mod63: Mod63;  // 人事记录分析模块
    }
    part def Mod61 {
        doc /* MOD-61 员工积分统计模块（module）：按工号查积分；条形图展示积分分布 */
        // 积分分值由奖惩产生（依赖 MOD-02 数据）
    }
    part def Mod62 {
        doc /* MOD-62 人事信息分析模块（module）：饼图人员分布：高校/职称/职位/党派/民族/学历/部门 */
    }
    part def Mod63 {
        doc /* MOD-63 人事记录分析模块（module）：离职率/离职工龄/离职年龄分析（柱状+折线） */
    }
    part def Mod07 {
        doc /* MOD-07 人事通讯模块（module）：操作员间点对点在线讯息 */
        // 依赖 WebSocket 接口（IF 见流程视图）
    }
    part def Mod08 {
        doc /* MOD-08 基础信息设置子系统（subsystem）：部门/职位/职称/奖惩规则/权限组管理 */
        part mod81: Mod81;  // 部门管理模块
        part mod82: Mod82;  // 职位管理模块
        part mod83: Mod83;  // 职称管理模块
        part mod84: Mod84;  // 奖惩规则管理模块
        part mod85: Mod85;  // 权限组管理模块
    }
    part def Mod81 {
        doc /* MOD-81 部门管理模块（module）：部门增删查改；部门树展示 */
    }
    part def Mod82 {
        doc /* MOD-82 职位管理模块（module）：职位增删查改 */
    }
    part def Mod83 {
        doc /* MOD-83 职称管理模块（module）：职称信息管理（细节待澄清） */
        // 对应待澄清项：是否与职位管理同构
    }
    part def Mod84 {
        doc /* MOD-84 奖惩规则管理模块（module）：奖惩规则设置与管理 */
        // 为 MOD-02 提供规则基础数据
    }
    part def Mod85 {
        doc /* MOD-85 权限组管理模块（module）：权限组设置；权限树展示 */
        // 为 MOD-10 RBAC 服务提供权限基础数据
    }
    part def Mod09 {
        doc /* MOD-09 系统管理子系统（subsystem）：操作员管理与授权处理 */
        part mod91: Mod91;  // 操作员管理模块
        part mod92: Mod92;  // 菜单权限配置模块
    }
    part def Mod91 {
        doc /* MOD-91 操作员管理模块（module）：操作员管理；为用户授予角色 */
    }
    part def Mod92 {
        doc /* MOD-92 菜单权限配置模块（module）：按角色分配菜单权限；前端默认不加载无权限菜单 */
    }
    part def Mod10 {
        doc /* MOD-10 RBAC 安全服务（service）：身份验证（自定义+表单验证）；RBAC 鉴权（URL 直达拦截）；操作审计日志；保密级别授权 */
        // 基于 RBAC0 模型（用户/角色映射/角色/权限/权限映射五表）；横切各业务模块
    }
    part def Mod20 {
        doc /* MOD-20 数据持久层（database）：员工主数据（1:N/1:1 关系）；RBAC 五表数据；培训考评数据；薪资账套数据 */
        // MySQL 8.0 存储；工号由数据库自动生成
    }
    part def Mod40 {
        doc /* MOD-40 前后端交互服务（service）：HTTP 前后端数据接口；WebSocket 在线讯息接口；Excel 导入导出接口 */
        // 前后端仅数据交互，页面跳转由前端路由处理
    }
}
