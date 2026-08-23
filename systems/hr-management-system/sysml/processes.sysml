package HrManagementSystemProcesses {
    action def prc001 {
        doc /* PRC-001 用户登录与访问控制流程：触发=管理员或操作员访问系统，参与者=用户, 系统 */
        action S01 {
            doc /* S01 [用户] 输入用户名密码提交登录表单 */
            // executes: MOD-92
        }
        action S02 {
            doc /* S02 [系统] 自定义验证与表单验证 */
            // executes: MOD-10
            // 异常：表单校验不通过→拦截并提示
        }
        action S03 {
            doc /* S03 [系统] 身份验证通过后获取当前用户的所有角色 */
            // executes: MOD-10
        }
        action S04 {
            doc /* S04 [系统] 根据角色加载对应的权限菜单（默认不加载无权限菜单） */
            // executes: MOD-92
        }
        action S05 {
            doc /* S05 [用户] 发起业务操作或直接输入 URL 访问 */
            // executes: MOD-11
        }
        action S06 {
            doc /* S06 [系统] 请求路径分析与 Spring Security 鉴权，判断角色是否可访问菜单资源 */
            // executes: MOD-10
            // 异常：未授权→拦截不放行
        }
        action S07 {
            doc /* S07 [系统] 放行响应资源并记录操作日志 */
            // executes: MOD-10
        }
        first S01 then S02;
        first S02 then S03;
        first S03 then S04;
        first S04 then S05;
        first S05 then S06;
        first S06 then S07;
        // S07 -> END
    }
    action def prc002 {
        doc /* PRC-002 员工入职建档流程：触发=新员工入职，参与者=HR */
        action S01 {
            doc /* S01 [HR] 在基本资料管理录入员工信息 */
            // executes: MOD-11
        }
        action S02 {
            doc /* S02 [系统] 必填项校验（工号以外全部必填） */
            // executes: MOD-11
            // 异常：必填缺失→表单校验拦截
        }
        action S03 {
            doc /* S03 [系统] 数据库自动生成员工工号 */
            // executes: MOD-20
        }
        action S04 {
            doc /* S04 [系统] 保存员工基本档案 */
            // executes: MOD-20
        }
        action S05 {
            doc /* S05 [HR] 维护高级资料（培训/考评/工资信息） */
            // executes: MOD-12
        }
        first S01 then S02;
        first S02 then S03;
        first S03 then S04;
        first S04 then S05;
        // S05 -> END
    }
    action def prc003 {
        doc /* PRC-003 员工奖惩办理流程：触发=员工获得奖励或处分，参与者=HR */
        action S01 {
            doc /* S01 [HR] 在奖惩管理中选择员工（穿梭框/tab） */
            // executes: MOD-21
        }
        action S02 {
            doc /* S02 [HR] 填写奖惩记录并保存（同一员工可多条 1:N） */
            // executes: MOD-21
        }
        action S03 {
            doc /* S03 [系统] 持久化奖惩记录 */
            // executes: MOD-20
        }
        action S04 {
            doc /* S04 [系统] 按奖惩规则自动累计员工积分 */
            // executes: MOD-61
        }
        action S05 {
            doc /* S05 [HR] 在奖惩管理列表查看有奖惩信息的员工与详情 */
            // executes: MOD-22
        }
        first S01 then S02;
        first S02 then S03;
        first S03 then S04;
        first S04 then S05;
        // S05 -> END
    }
    action def prc004 {
        doc /* PRC-004 员工培训办理流程：触发=员工参加培训，参与者=HR */
        action S01 {
            doc /* S01 [HR] 批量添加员工培训 */
            // executes: MOD-31
        }
        action S02 {
            doc /* S02 [系统] 在训唯一约束校验（同一员工同期仅一个培训） */
            // executes: MOD-31
            // 异常：同期已有在训培训→拒绝添加
        }
        action S03 {
            doc /* S03 [系统] 保存培训记录并展示进度条 */
            // executes: MOD-31
        }
        action S04 {
            doc /* S04 [HR] 更新培训进度 */
            // executes: MOD-31
        }
        action S05 {
            doc /* S05 [HR] 培训完成后删除当前培训记录（方可添加新培训） */
            // executes: MOD-31
        }
        first S01 then S02;
        first S02 then S03;
        first S03 then S04;
        first S04 then S05;
        // S05 -> END
    }
    action def prc005 {
        doc /* PRC-005 员工考评办理流程：触发=考评周期到达，参与者=HR */
        action S01 {
            doc /* S01 [HR] 批量添加员工评价（评分条/步骤条界面） */
            // executes: MOD-32
        }
        action S02 {
            doc /* S02 [系统] 一对一关系校验（员工与考评 1:1） */
            // executes: MOD-32
            // 异常：该员工已有考评→不可重复
        }
        action S03 {
            doc /* S03 [系统] 保存考评结果（考评日期/内容/结果） */
            // executes: MOD-20
        }
        first S01 then S02;
        first S02 then S03;
        // S03 -> END
    }
    action def prc006 {
        doc /* PRC-006 员工调动办理流程：触发=员工岗位/部门变动，参与者=HR */
        action S01 {
            doc /* S01 [HR] 选择员工并填写调动信息（table 内嵌 table） */
            // executes: MOD-04
        }
        action S02 {
            doc /* S02 [系统] 保存调动记录（员工与调动 1:N） */
            // executes: MOD-20
        }
        first S01 then S02;
        // S02 -> END
    }
    action def prc007 {
        doc /* PRC-007 工资管理流程：触发=薪资设定与发放周期，参与者=HR, 财务 */
        action S01 {
            doc /* S01 [HR] 维护工资账套各项（奖金/基本工资/提成） */
            // executes: MOD-51
        }
        action S02 {
            doc /* S02 [HR] 设置当前套账 */
            // executes: MOD-51
        }
        action S03 {
            doc /* S03 [HR] 为员工设置工资账套 */
            // executes: MOD-52
        }
        action S04 {
            doc /* S04 [财务] 工资表查询与筛选（按职称/部门），查看套账详情 */
            // executes: MOD-53
        }
        first S01 then S02;
        first S02 then S03;
        first S03 then S04;
        // S04 -> END
    }
    action def prc008 {
        doc /* PRC-008 前端请求统一处理流程：触发=任意前端操作触发请求，参与者=系统 */
        action S01 {
            doc /* S01 [系统] 用户操作触发前端请求 */
            // executes: MOD-92
        }
        action S02 {
            doc /* S02 [系统] 前端拦截器统一拦截所有请求 */
            // executes: MOD-40
        }
        action S03 {
            doc /* S03 [系统] 后端返回数据或消息，前端分析需要返回数据还是消息 */
            // executes: MOD-40
        }
        first S01 then S02;
        first S02 then S03;
        // S03 -> END
    }
    // interface IF-01 登录认证接口：MOD-10 -> MOD-92（自定义验证+表单验证/HTTP）登录请求(request: 用户名, 密码)；鉴权结果(response: 用户角色列表, 权限菜单)
    // interface IF-02 在线讯息接口：MOD-40 -> MOD-07（WebSocket 双向通信/WebSocket）讯息报文(request: 发送者, 接收者, 讯息内容)
    // interface IF-03 Excel 导入导出接口：MOD-40 -> MOD-11（文件流/HTTP）导入文件(request: 员工基本资料 Excel)；导出文件(response: 员工基本资料 Excel)
    // interface IF-04 业务数据接口：MOD-40 -> MOD-11, MOD-21, MOD-31, MOD-51, MOD-53, MOD-61, MOD-62（REST 风格/HTTP）业务请求(request: 资源路径, 参数)；数据或消息(response: 业务数据, 处理消息)
    // dataflow DF-01：MOD-21 -> MOD-20（奖惩记录，实时）
    // dataflow DF-02：MOD-20 -> MOD-61（奖惩积分数据，奖惩事件触发）
    // dataflow DF-03：MOD-51 -> MOD-20（工资账套定义与当前套账，实时）
    // dataflow DF-04：MOD-20 -> MOD-53（工资表数据（按职称/部门筛选），按需查询）
    // dataflow DF-05：MOD-20 -> MOD-62（人事维度分布数据（7 维），按需查询）
    // dataflow DF-06：MOD-11 -> MOD-12（员工档案与高级资料关联，实时）
}
