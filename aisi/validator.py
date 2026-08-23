"""零依赖 JSON Schema 校验器（draft-07 子集）。

支持关键字：type / const / enum / pattern / minLength / minItems / minimum /
required / properties / additionalProperties / items / definitions / $ref（仅本地）。
Schema 文件是唯一契约事实源，本模块使其无需第三方依赖即可在任何宿主环境运行。
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict:
    p = SCHEMA_DIR / f"{name}.schema.json"
    if not p.exists():
        raise FileNotFoundError(f"未找到契约 {name}（{p}）")
    return json.loads(p.read_text(encoding="utf-8"))


def list_schemas() -> list[str]:
    return sorted(p.name.removesuffix(".schema.json") for p in SCHEMA_DIR.glob("*.schema.json"))


def _type_ok(v, t: str) -> bool:
    if t == "object":
        return isinstance(v, dict)
    if t == "array":
        return isinstance(v, list)
    if t == "string":
        return isinstance(v, str)
    if t == "boolean":
        return isinstance(v, bool)
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if t == "null":
        return v is None
    return True


def _err(path: str, code: str, message: str, suggestion: str = "") -> dict:
    return {"path": path, "code": code, "message": message, "suggestion": suggestion}


def validate(instance, schema: dict, root: dict | None = None, path: str = "$") -> list[dict]:
    """返回错误列表（空列表 = 通过）。"""
    root = root if root is not None else schema
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [_err(path, "unsupported_ref", f"仅支持本地 $ref: {ref}")]
        target: dict = root
        try:
            for part in ref[2:].split("/"):
                target = target[part]
        except (KeyError, TypeError):
            return [_err(path, "bad_ref", f"$ref 无法解析: {ref}")]
        return validate(instance, target, root, path)

    errors: list[dict] = []
    t = schema.get("type")
    if t and not _type_ok(instance, t):
        want = t if isinstance(t, str) else "/".join(t)
        got = type(instance).__name__
        return [_err(path, "type", f"类型应为 {want}，实际 {got}")]

    if "const" in schema and instance != schema["const"]:
        errors.append(_err(path, "const", f"必须等于 {schema['const']!r}"))
    if "enum" in schema and instance not in schema["enum"]:
        allowed = "、".join(str(x) for x in schema["enum"])
        errors.append(_err(path, "enum", f"取值 {instance!r} 不在允许集合", f"允许值：{allowed}"))
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(_err(path, "pattern", f"不匹配格式 {schema['pattern']}",
                               "示例：REQ-001 / MOD-01 / LAY-01 / PRC-001"))
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(_err(path, "minLength", f"长度不足，最少 {schema['minLength']} 字符"))
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(_err(path, "minimum", f"应 >= {schema['minimum']}"))
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(_err(path, "minItems", f"至少 {schema['minItems']} 项"))
        if "items" in schema:
            for i, item in enumerate(instance):
                errors += validate(item, schema["items"], root, f"{path}[{i}]")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(_err(path, "required", f"缺少必填字段 {key!r}",
                                   f"在 {path} 对象中补充 {key} 字段"))
        props = schema.get("properties", {})
        for k, v in instance.items():
            if k in props:
                errors += validate(v, props[k], root, f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errors.append(_err(f"{path}.{k}", "additionalProperty",
                                   f"字段 {k!r} 不在契约定义中", "删除或改用契约内字段"))
    return errors
