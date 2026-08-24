---
id: KB-2026-0006
type: domain
title: 调研：调研行业典型值或与用户确认 REQ-002 的量化指标（数值+单位+条件）
tags: [research, hr-management-system]
source: aisi research（hr-management-system）
created: 2026-08-24
status: active
supersedes: ""
confidence: medium
---

## 内容

- 建议 REQ-002（性能需求组）采用系统级指标：页面加载时间 <=3s、常规查询响应 <=1s；与低配运行环境（单核 2G）条件绑定。（置信度：high，来源：WEB-004, WEB-005, WEB-006）

## 来源

- WEB-004 亚马逊云科技：网站响应时间行业标准（2s 内可接受，3s 以上用户流失）：https://www.amazonaws.cn/what-is/website-response-time（high，2026-08-24）
- WEB-005 压力测试核心性能指标及行业标准（核心接口<500ms，普通<1s，特殊<=3s）：https://testerhome.com/topics/37119（medium，2026-08-24）
- WEB-006 国家标准《城镇供水管网智能化通用技术要求》（核心业务<=3s，非核心3~5s）：https://std.samr.gov.cn/dcpspTools/gbPlan/download?path=%2Fzxd%2F2024006334%2F20_%E6%A0%87%E5%87%86%E8%B5%B7%E8%8D%89%2F20_WD_2024006334_%E5%9F%8E%E9%95%87%E4%BE%9B%E6%B0%B4%E7%AE%A1%E7%BD%91%E6%99%BA%E8%83%BD%E5%8C%96%E9%80%9A%E7%94%A8%E6%8A%80%E6%9C%AF%E8%A6%81%E6%B1%82.pdf（high，2026-08-24）

## 适用场景

人力资源管理系统 系统设计与需求完善时参考。
