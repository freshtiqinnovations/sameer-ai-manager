import os
import shutil
from datetime import datetime

BASE = "/root/sameer_ai_manager/upgrades"

PENDING = f"{BASE}/pending"
APPROVED = f"{BASE}/approved"
REJECTED = f"{BASE}/rejected"
APPLIED = f"{BASE}/applied"


def ensure_dirs():
    for d in [PENDING, APPROVED, REJECTED, APPLIED]:
        os.makedirs(d, exist_ok=True)


def create_patch(name, content):
    ensure_dirs()

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.txt"

    path = os.path.join(PENDING, filename)

    with open(path, "w") as f:
        f.write(content)

    return path


def approve_patch(filename):
    src = os.path.join(PENDING, filename)
    dst = os.path.join(APPROVED, filename)

    if os.path.exists(src):
        shutil.move(src, dst)
        return True

    return False


def reject_patch(filename):
    src = os.path.join(PENDING, filename)
    dst = os.path.join(REJECTED, filename)

    if os.path.exists(src):
        shutil.move(src, dst)
        return True

    return False


def apply_patch(filename):
    src = os.path.join(APPROVED, filename)
    dst = os.path.join(APPLIED, filename)

    if os.path.exists(src):
        shutil.move(src, dst)
        return True

    return False


if __name__ == "__main__":
    ensure_dirs()
    print("Upgrade manager ready")
