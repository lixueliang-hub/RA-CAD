import json
import sys
import traceback

import cadquery as cq
from cadquery import exporters


def main() -> None:
    code_path = sys.argv[1]
    stl_path = sys.argv[2]
    #终端执行命令python cad_executor.py ./temp/code_123.py ./output/model_123.stl

    code = open(code_path, "r", encoding="utf-8").read()

    # 注意：生产环境应放在容器/受限子进程中执行，
    # 这里只演示最小执行器。
    env = {
        "__name__": "__main__",
        "cq": cq,
        "cadquery": cq,
    }

    try:
        exec(compile(code, "<cad_code>", "exec"), env, env)
        obj = env.get("result")

        if obj is None:
            raise ValueError("The code did not assign a Workplane to `result`.")

        shape = obj.val() if hasattr(obj, "val") else obj
        exporters.export(shape, stl_path)

        print(json.dumps({"ok": True, "error": ""}))
    except Exception:
        print(json.dumps({
            "ok": False,
            "error": traceback.format_exc(limit=5),
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()