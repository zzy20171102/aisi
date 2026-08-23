package HrManagementSystemRequirements {
    requirement <'REQ-001'> req001 {
        doc /* REQ-001 功能需求：系统应提供员工资料、奖惩、培训考评、调动、薪资、统计分析、在线通讯、基础信息设置与系统管理等功能。 */
        // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
        // 来源：SRC-001#二
        requirement <'REQ-001.1'> req001_1 {
            doc /* REQ-001.1 员工资料管理：系统应支持员工资料管理，包括基本资料的增删改查与高级资料（培训、考评、工资）的查询。 */
            // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#项目介绍, SRC-001#4.3
            requirement <'REQ-001.1.1'> req001_1_1 {
                doc /* REQ-001.1.1 基本资料管理：系统应支持员工基本资料的增删改查与批量导入导出。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#4.3.1
                requirement <'REQ-001.1.1.1'> req001_1_1_1 {
                    doc /* REQ-001.1.1.1 档案增删改查：系统应实现对员工基本资料的增删改查；修改操作根据 id 进行数据更新。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                    // 来源：SRC-001#4.3.1
                }
                requirement <'REQ-001.1.1.2'> req001_1_1_2 {
                    doc /* REQ-001.1.1.2 工号自动生成：添加员工时工号应由数据库自动生成，无需人工录入。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                    // 来源：SRC-001#4.3.1
                }
                requirement <'REQ-001.1.1.3'> req001_1_1_3 {
                    doc /* REQ-001.1.1.3 必填项校验：工号以外的员工基本资料信息应为必填项。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                    // 来源：SRC-001#4.3.1
                }
                requirement <'REQ-001.1.1.4'> req001_1_1_4 {
                    doc /* REQ-001.1.1.4 多条件搜索：系统应支持按多个条件组合搜索员工基本资料。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                    // 来源：SRC-001#4.3.1
                }
            }
            requirement <'REQ-001.1.2'> req001_1_2 {
                doc /* REQ-001.1.2 高级资料查询：系统应支持员工高级资料的查询，高级资料由培训资料、考评资料、工资信息三部分构成。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#4.3.2
                requirement <'REQ-001.1.2.1'> req001_1_2_1 {
                    doc /* REQ-001.1.2.1 培训资料查询：系统应支持查询员工培训资料，内容包含培训日期、培训内容。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                    // 来源：SRC-001#4.3.2
                }
                requirement <'REQ-001.1.2.2'> req001_1_2_2 {
                    doc /* REQ-001.1.2.2 考评资料查询：系统应支持查询员工考评资料，内容包含考评日期、考评内容、考评结果。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                    // 来源：SRC-001#4.3.2
                }
                requirement <'REQ-001.1.2.3'> req001_1_2_3 {
                    doc /* REQ-001.1.2.3 工资信息查询：系统应支持查询员工工资信息，内容包含账套名称、基本工资。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                    // 来源：SRC-001#4.3.2
                }
            }
        }
        requirement <'REQ-001.2'> req001_2 {
            doc /* REQ-001.2 员工奖惩管理：系统应支持员工奖惩信息管理，员工实体与奖惩信息为一对多关系。 */
            // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#4
            requirement <'REQ-001.2.1'> req001_2_1 {
                doc /* REQ-001.2.1 添加奖惩：系统应支持为员工添加奖惩记录，同一员工可添加多条。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#4.1
            }
            requirement <'REQ-001.2.2'> req001_2_2 {
                doc /* REQ-001.2.2 奖惩管理列表：奖惩管理页面应显示有奖惩信息的全部员工，并支持查看奖惩详情。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                // 来源：SRC-001#4.2
            }
        }
        requirement <'REQ-001.3'> req001_3 {
            doc /* REQ-001.3 员工培训与考评：系统应支持员工培训业务与员工评价业务的增删改查。 */
            // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#5
            requirement <'REQ-001.3.1'> req001_3_1 {
                doc /* REQ-001.3.1 培训管理：系统应支持添加培训、培训管理、培训进度维护。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#5.1, SRC-001#5.2
                requirement <'REQ-001.3.1.1'> req001_3_1_1 {
                    doc /* REQ-001.3.1.1 批量添加培训：系统应支持批量添加员工培训。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                    // 来源：SRC-001#5.2
                }
                requirement <'REQ-001.3.1.2'> req001_3_1_2 {
                    doc /* REQ-001.3.1.2 在训唯一约束：同一员工在一个时间段只能参加一个培训；培训完成删除当前培训后方可添加新培训。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                    // 来源：SRC-001#5.2
                }
                requirement <'REQ-001.3.1.3'> req001_3_1_3 {
                    doc /* REQ-001.3.1.3 培训进度管理：系统应支持培训进度的修改与进度条展示。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                    // 来源：SRC-001#5.2
                }
            }
            requirement <'REQ-001.3.2'> req001_3_2 {
                doc /* REQ-001.3.2 考评管理：系统应支持员工评价业务的增删改查，员工与考评为一对一关系。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#5.3, SRC-001#5.4
                requirement <'REQ-001.3.2.1'> req001_3_2_1 {
                    doc /* REQ-001.3.2.1 批量添加考评：系统应支持批量添加员工评价，界面采用评分条与步骤条。 */
                    // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                    // 来源：SRC-001#5.4
                }
            }
        }
        requirement <'REQ-001.4'> req001_4 {
            doc /* REQ-001.4 员工调动管理：系统应支持员工调动信息的增删改查，员工与调动信息为一对多关系。 */
            // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#6
        }
        requirement <'REQ-001.5'> req001_5 {
            doc /* REQ-001.5 薪资管理：系统应支持员工工资账套管理、员工账套设置、工资表管理一系列工资管理功能。 */
            // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#7
            requirement <'REQ-001.5.1'> req001_5_1 {
                doc /* REQ-001.5.1 工资账套管理：系统应支持对员工奖金、基本工资、提成等各项的增删改查，并设置当前套账信息。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#7
            }
            requirement <'REQ-001.5.2'> req001_5_2 {
                doc /* REQ-001.5.2 员工账套设置：系统应支持为员工设置工资账套。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#8
            }
            requirement <'REQ-001.5.3'> req001_5_3 {
                doc /* REQ-001.5.3 工资表管理：系统应支持员工工资的搜索查看，可根据不同职称、部门进行表内筛选，并查看工资套账详情。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                // 来源：SRC-001#9
            }
        }
        requirement <'REQ-001.6'> req001_6 {
            doc /* REQ-001.6 统计分析：系统应支持员工积分统计、人事信息分析与人事记录分析。 */
            // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
            // 来源：SRC-001#10, SRC-001#11, SRC-001#12
            requirement <'REQ-001.6.1'> req001_6_1 {
                doc /* REQ-001.6.1 员工积分统计：系统应支持根据工号查找员工积分情况，以条形图显示有积分员工的积分分布；积分分值由员工奖惩产生。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                // 来源：SRC-001#10
            }
            requirement <'REQ-001.6.2'> req001_6_2 {
                doc /* REQ-001.6.2 人事信息分析：系统应以饼图方式展示员工人数分布，支持按高校、职称、职位、党派、民族、学历、部门维度统计。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                // 来源：SRC-001#11
            }
            requirement <'REQ-001.6.3'> req001_6_3 {
                doc /* REQ-001.6.3 人事记录分析：系统应支持员工离职信息统计，按部门、职称、职位维度对离职率、离职工龄、离职年龄进行分析，以柱状图结合折线图展示。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                // 来源：SRC-001#12
            }
        }
        requirement <'REQ-001.7'> req001_7 {
            doc /* REQ-001.7 人事通讯：系统应实现操作员之间点对点在线讯息的及时通讯。 */
            // 属性：type=functional ｜ priority=应当 ｜ verification=演示 ｜ status=confirmed
            // 来源：SRC-001#项目介绍
        }
        requirement <'REQ-001.8'> req001_8 {
            doc /* REQ-001.8 基础信息设置：系统应支持基础信息设置，包括部门、职位、职称、奖惩规则和权限组的管理。 */
            // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#12基础信息设置
            requirement <'REQ-001.8.1'> req001_8_1 {
                doc /* REQ-001.8.1 部门管理：系统应支持部门的增删查改，并以部门树形式展示组织结构。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#12.1
            }
            requirement <'REQ-001.8.2'> req001_8_2 {
                doc /* REQ-001.8.2 职位管理：系统应支持职位的增删查改。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#12.2
            }
            requirement <'REQ-001.8.3'> req001_8_3 {
                doc /* REQ-001.8.3 职称管理：系统应支持职称信息的管理。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#12基础信息设置
                // 待澄清：报告未展开职称管理细节，是否与职位管理同构？（待答复）
            }
            requirement <'REQ-001.8.4'> req001_8_4 {
                doc /* REQ-001.8.4 奖惩规则管理：系统应支持奖惩规则的设置与管理。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#12基础信息设置
            }
            requirement <'REQ-001.8.5'> req001_8_5 {
                doc /* REQ-001.8.5 权限组管理：系统应支持权限组的设置与管理，并以权限树形式展示。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#12基础信息设置
            }
        }
        requirement <'REQ-001.9'> req001_9 {
            doc /* REQ-001.9 系统管理：系统应支持系统管理、管理员操作，包括基础设置、系统管理、操作员管理、授权处理。 */
            // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#12系统管理
            requirement <'REQ-001.9.1'> req001_9_1 {
                doc /* REQ-001.9.1 操作员管理：系统应支持操作员管理，为不同用户授予不同角色。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
                // 来源：SRC-001#12系统管理, SRC-001#二
            }
            requirement <'REQ-001.9.2'> req001_9_2 {
                doc /* REQ-001.9.2 菜单权限配置：系统管理应可根据不同角色分配菜单权限设置；为良好用户体验，前端默认不加载无权限菜单。 */
                // 属性：type=functional ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
                // 来源：SRC-001#2.1
            }
        }
    }
    requirement <'REQ-002'> req002 {
        doc /* REQ-002 性能需求：系统应满足操作响应与低资源配置下的运行性能要求。 */
        // 属性：type=performance ｜ priority=应当 ｜ verification=测试 ｜ status=confirmed
        // 来源：SRC-001#1.1
        requirement <'REQ-002.1'> req002_1 {
            doc /* REQ-002.1 操作响应性能：系统应由前端视图操作通知、结合后端逻辑处理消息构成用户体验处理，响应用户的每一步操作。 */
            // 属性：type=performance ｜ priority=应当 ｜ verification=演示 ｜ status=confirmed
            // 来源：SRC-001#1.1
            // 待澄清：报告未给出量化响应指标（如页面响应时间上限），是否需要补充？（待答复）
        }
        requirement <'REQ-002.2'> req002_2 {
            doc /* REQ-002.2 低配运行能力：系统应在普通单核 CPU、2G RAM 的 ECS 环境下满足运行性能需求。 */
            // 属性：type=performance ｜ priority=应当 ｜ verification=测试 ｜ status=confirmed ｜ 运行内存=<=2GB
            // 来源：SRC-001#1.1
        }
    }
    requirement <'REQ-003'> req003 {
        doc /* REQ-003 数据需求：系统应管理员工主数据、权限模型数据、培训考评数据、薪资数据、奖惩积分数据、统计维度数据与基础信息数据，并支持 Excel 数据交换。 */
        // 属性：type=data ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
        // 来源：SRC-001#二, SRC-001#4.3.2
        requirement <'REQ-003.1'> req003_1 {
            doc /* REQ-003.1 员工主数据：系统应维护员工基本资料主数据：工号自动生成、其余字段必填；员工与奖惩信息一对多、与调动信息一对多、与在训培训一对一、与考评一对一。 */
            // 属性：type=data ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#4.3.1, SRC-001#4, SRC-001#5, SRC-001#6
        }
        requirement <'REQ-003.2'> req003_2 {
            doc /* REQ-003.2 权限数据模型：系统应维护 RBAC0 模型对应的五类数据实体：用户表、角色映射表、角色表、权限表、权限映射表。 */
            // 属性：type=data ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#2.1
        }
        requirement <'REQ-003.3'> req003_3 {
            doc /* REQ-003.3 培训与考评数据：系统应维护培训资料（培训日期、培训内容、培训进度）与考评资料（考评日期、考评内容、考评结果）数据。 */
            // 属性：type=data ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#4.3.2, SRC-001#5
        }
        requirement <'REQ-003.4'> req003_4 {
            doc /* REQ-003.4 薪资数据：系统应维护工资账套数据（奖金、基本工资、提成各项）、员工与账套的关联关系及工资表数据。 */
            // 属性：type=data ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#7, SRC-001#8, SRC-001#9
        }
        requirement <'REQ-003.5'> req003_5 {
            doc /* REQ-003.5 奖惩与积分数据：系统应维护员工奖惩记录数据；员工积分分值应由奖惩数据产生。 */
            // 属性：type=data ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#10
        }
        requirement <'REQ-003.6'> req003_6 {
            doc /* REQ-003.6 统计维度数据：系统应维护人事统计维度数据：高校、职称、职位、党派、民族、学历、部门，以及离职率、离职工龄、离职年龄。 */
            // 属性：type=data ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#11, SRC-001#12
        }
        requirement <'REQ-003.7'> req003_7 {
            doc /* REQ-003.7 基础信息数据：系统应维护部门树、职位、职称、奖惩规则、权限组等基础信息数据。 */
            // 属性：type=data ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#12基础信息设置
        }
        requirement <'REQ-003.8'> req003_8 {
            doc /* REQ-003.8 数据交换格式：系统应支持员工基本资料表的 Excel 导入导出数据格式。 */
            // 属性：type=data ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#4.3.1
        }
    }
    requirement <'REQ-004'> req004 {
        doc /* REQ-004 部署需求：系统应满足 B/S 架构、前后端分离的低成本部署要求。 */
        // 属性：type=deployment ｜ priority=应当 ｜ verification=测试 ｜ status=confirmed
        // 来源：SRC-001#1.1, SRC-001#二
        requirement <'REQ-004.1'> req004_1 {
            doc /* REQ-004.1 部署形态：系统应采用 B/S 架构与前后端分离部署：前端作为独立 Server，后端使用 Spring Boot 内嵌 Tomcat 服务器，页面跳转由前端路由处理，前后端仅进行数据交互。 */
            // 属性：type=deployment ｜ priority=应当 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#二, SRC-001#4技术栈
        }
        requirement <'REQ-004.2'> req004_2 {
            doc /* REQ-004.2 服务器运行环境：系统应可部署于普通单核 CPU、2G RAM 的 ECS 服务器。 */
            // 属性：type=deployment ｜ priority=应当 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#1.1
        }
        requirement <'REQ-004.3'> req004_3 {
            doc /* REQ-004.3 安装包大小：系统打包后整体大小应约为 38MB，硬件内存需求相当于普通移动端 App 大小。 */
            // 属性：type=deployment ｜ priority=应当 ｜ verification=测试 ｜ status=confirmed ｜ 安装包大小==38MB
            // 来源：SRC-001#1.1
        }
        requirement <'REQ-004.4'> req004_4 {
            doc /* REQ-004.4 客户端浏览器环境：系统应兼容大部分浏览器访问，包括 IE 8/9/10/11、Chrome、Firefox。 */
            // 属性：type=deployment ｜ priority=应当 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#1.1
        }
        requirement <'REQ-004.5'> req004_5 {
            doc /* REQ-004.5 数据库环境：系统应使用 MySQL 8.0 数据库存储数据。 */
            // 属性：type=deployment ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#4技术栈
        }
    }
    requirement <'REQ-005'> req005 {
        doc /* REQ-005 安全需求：系统应实现基于 RBAC 的访问控制、身份验证与操作留痕，保障人事信息保密。 */
        // 属性：type=security ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
        // 来源：SRC-001#1
        requirement <'REQ-005.1'> req005_1 {
            doc /* REQ-005.1 身份验证：管理员或操作员须经自定义验证与表单验证通过后方可进入系统。 */
            // 属性：type=security ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#2
        }
        requirement <'REQ-005.2'> req005_2 {
            doc /* REQ-005.2 RBAC鉴权：用户登录后应获取其所有角色并加载对应权限菜单；对直接输入 URL 的每一个请求，都应通过鉴权处理并判断是否可访问菜单资源。 */
            // 属性：type=security ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#2.1
        }
        requirement <'REQ-005.3'> req005_3 {
            doc /* REQ-005.3 操作审计日志：管理员对系统的操作应全部记录在日志里。 */
            // 属性：type=security ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#2
        }
        requirement <'REQ-005.4'> req005_4 {
            doc /* REQ-005.4 保密级别授权：对不同操作员角色应根据保密级别给予不同权限。 */
            // 属性：type=security ｜ priority=必须 ｜ verification=审查 ｜ status=confirmed
            // 来源：SRC-001#1
        }
    }
    requirement <'REQ-006'> req006 {
        doc /* REQ-006 接口需求：系统应提供前后端数据接口、在线讯息接口与数据导入导出接口。 */
        // 属性：type=interface ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
        // 来源：SRC-001#二, SRC-001#1.2
        requirement <'REQ-006.1'> req006_1 {
            doc /* REQ-006.1 前后端数据接口：前后端应通过接口使用 HTTP 协议交互，仅进行数据的交互，页面跳转不再由后端处理。 */
            // 属性：type=interface ｜ priority=必须 ｜ verification=测试 ｜ status=confirmed
            // 来源：SRC-001#二
        }
        requirement <'REQ-006.2'> req006_2 {
            doc /* REQ-006.2 在线讯息接口：系统应基于 WebSocket 提供操作员之间点对点在线讯息通信接口。 */
            // 属性：type=interface ｜ priority=应当 ｜ verification=演示 ｜ status=confirmed
            // 来源：SRC-001#1.2
        }
        requirement <'REQ-006.3'> req006_3 {
            doc /* REQ-006.3 数据导入导出接口：系统应提供员工基本资料 Excel 导入与导出接口。 */
            // 属性：type=interface ｜ priority=必须 ｜ verification=演示 ｜ status=confirmed
            // 来源：SRC-001#4.3.1
        }
    }
}
