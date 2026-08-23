package HrManagementSystemArchitecture {
    package LAY01应用层（前端应用） {
        doc /* LAY-01 应用层（前端应用）（第1层）：MVVM 模式 Vue.js 单页应用（SPA），前后端分离，页面跳转由 vue-router 前端路由处理 */
        // 技术栈：Vue.js, ElementUI, vue-router, axios, JavaScript
        // allocate: MOD-11
        // allocate: MOD-12
        // allocate: MOD-21
        // allocate: MOD-22
        // allocate: MOD-31
        // allocate: MOD-32
        // allocate: MOD-04
        // allocate: MOD-51
        // allocate: MOD-52
        // allocate: MOD-53
        // allocate: MOD-61
        // allocate: MOD-62
        // allocate: MOD-63
        // allocate: MOD-07
        // allocate: MOD-81
        // allocate: MOD-82
        // allocate: MOD-83
        // allocate: MOD-84
        // allocate: MOD-85
        // allocate: MOD-91
        // allocate: MOD-92
    }
    package LAY02接口层（前后端交互服务） {
        doc /* LAY-02 接口层（前后端交互服务）（第2层）：前后端仅进行数据交互：HTTP 协议接口、WebSocket 在线讯息、Excel 数据导入导出 */
        // 技术栈：HTTP/REST, WebSocket, 文件流（Excel）
        // allocate: MOD-40
    }
    package LAY03业务逻辑层（后端服务） {
        doc /* LAY-03 业务逻辑层（后端服务）（第3层）：Spring Boot 内嵌 Tomcat 承载后端业务逻辑与安全框架；基于 Servlet Filter 原理实现鉴权 */
        // 技术栈：Java 8, Spring Boot（IOC/MVC/ORM）, Spring Security, MyBatis
        // allocate: MOD-10
    }
    package LAY04数据层（持久化存储） {
        doc /* LAY-04 数据层（持久化存储）（第4层）：MySQL 关系数据库存储；工号由数据库自动生成；RBAC 五表模型 */
        // 技术栈：MySQL 8.0, RBAC0 五表模型
        // allocate: MOD-20
    }
    // service SVC-01 RBAC 权限服务（business）挂载 MOD-10：Spring Security 过滤器链（鉴权基于 Servlet Filter 原理，授权由系统管理员操作）
    // service SVC-02 WebSocket 在线讯息服务（business）挂载 MOD-40：WebSocket 双向通信
    // service SVC-03 Excel 导入导出服务（data）挂载 MOD-40：文件流导入导出接口
    // service SVC-04 统计分析数据服务（data）挂载 MOD-06：后端统计聚合查询
    // service SVC-05 MySQL 数据库服务（data）挂载 MOD-20：MySQL 8.0
    item def da01 {
        doc /* DA-01 员工主数据：Employee（员工）, RewardPenalty（奖惩）, Transfer（调动）, Training（培训）, Appraisal（考评）（MySQL 8.0，归属 MOD-20，敏感级 机密） */
    }
    item def da02 {
        doc /* DA-02 RBAC 权限数据：User（用户表）, RoleMapping（角色映射表）, Role（角色表）, Permission（权限表）, PermissionMapping（权限映射表）（MySQL 8.0，归属 MOD-10，敏感级 机密） */
    }
    item def da03 {
        doc /* DA-03 薪资数据：SalaryAccount（工资账套：奖金/基本工资/提成）, EmployeeAccount（员工账套设置）, Payroll（工资表）（MySQL 8.0，归属 MOD-05，敏感级 机密） */
    }
    item def da04 {
        doc /* DA-04 统计维度数据：高校/职称/职位/党派/民族/学历/部门维度, 离职记录（离职率/工龄/年龄）（MySQL 8.0，归属 MOD-06，敏感级 内部） */
    }
    item def da05 {
        doc /* DA-05 基础信息数据：Department（部门树）, Position（职位）, Title（职称）, RewardRule（奖惩规则）, PermissionGroup（权限组树）（MySQL 8.0，归属 MOD-08，敏感级 内部） */
    }
    // deploy N-01 应用服务器（ECS）：普通单核 CPU、2G RAM（原文表述 ESC，按 ECS 理解）（承载 SVC-01, SVC-02, SVC-03, SVC-04）
    // deploy N-02 数据库服务器：MySQL 8.0（承载 SVC-05）
    // deploy N-03 客户端浏览器：IE 8/9/10/11、Chrome、Firefox（承载 客户端）
}
