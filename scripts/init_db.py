#!/usr/bin/env python3
"""
BugTracer Database Initialization & Management Script
Usage:
    python scripts/init_db.py               # Initialize tables & default admin/project
    python scripts/init_db.py --seed-demo   # Initialize and seed demo data
    python scripts/init_db.py --reset       # Reset and re-initialize entire database
"""
import sys
import os
import asyncio
import argparse

# Ensure project root is in sys.path and set as current working directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

from backend.app.core.config import settings
from backend.app.core.database import init_db, engine, Base, AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.project import Project, ProjectMember
from backend.app.models.module import Module
from backend.app.models.bug import Bug
from backend.app.core.security import hash_password, generate_api_key
from sqlalchemy import select

async def reset_database():
    print("⚠️  Dropping all existing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("✅ All tables dropped.")

async def seed_demo_data():
    print("🌱 Seeding demo bugs and modules...")
    async with AsyncSessionLocal() as session:
        # Find project 1
        stmt = select(Project).where(Project.id == 1)
        res = await session.execute(stmt)
        project = res.scalars().first()
        if not project:
            print("❌ Project 1 not found.")
            return

        # Find or create modules
        mod_names = ["用户中心", "订单支付", "工作台看板"]
        modules = []
        for idx, name in enumerate(mod_names, start=2):
            mod_stmt = select(Module).where(Module.project_id == project.id, Module.name == name)
            mod_res = await session.execute(mod_stmt)
            mod = mod_res.scalars().first()
            if not mod:
                mod = Module(project_id=project.id, name=name, sort_order=idx)
                session.add(mod)
                await session.flush()
            modules.append(mod)

        # Create demo developer
        dev_stmt = select(User).where(User.username == "coder1")
        dev_res = await session.execute(dev_stmt)
        coder = dev_res.scalars().first()
        if not coder:
            coder = User(
                username="coder1",
                password_hash=hash_password("123456"),
                fullname="开发小李",
                role="coder",
                api_key=generate_api_key("bt_"),
                is_active=True
            )
            session.add(coder)
            await session.flush()
            session.add(ProjectMember(project_id=project.id, user_id=coder.id, role="coder"))

        # Create demo tester
        test_stmt = select(User).where(User.username == "tester1")
        test_res = await session.execute(test_stmt)
        tester = test_res.scalars().first()
        if not tester:
            tester = User(
                username="tester1",
                password_hash=hash_password("123456"),
                fullname="测试小张",
                role="tester",
                api_key=generate_api_key("bt_"),
                is_active=True
            )
            session.add(tester)
            await session.flush()
            session.add(ProjectMember(project_id=project.id, user_id=tester.id, role="tester"))

        # Check existing bugs
        bug_count_stmt = select(Bug).where(Bug.project_id == project.id)
        bug_count_res = await session.execute(bug_count_stmt)
        if not bug_count_res.scalars().first():
            demo_bugs = [
                Bug(
                    project_id=project.id,
                    module_id=modules[0].id,
                    content="登录页面在弱网环境下点击提交按钮无 Loading 状态反馈，导致用户重复点击报错",
                    status=1,
                    priority=1,
                    ver="v2.0.0",
                    creator_id=tester.id if tester else 1,
                    assignee_id=coder.id if coder else 0,
                    last_changer_id=tester.id if tester else 1
                ),
                Bug(
                    project_id=project.id,
                    module_id=modules[1].id,
                    content="[b]支付回调超时[/b]：微信支付异步通知偶发性验签失败，需增加重试机制与幂等处理",
                    status=2,
                    priority=2,
                    ver="v2.0.0",
                    creator_id=1,
                    assignee_id=coder.id if coder else 0,
                    last_changer_id=1
                ),
                Bug(
                    project_id=project.id,
                    module_id=modules[2].id,
                    content="工作台支持自定义模块拖拽排序及默认筛选视图持久化保存",
                    status=7,
                    priority=0,
                    ver="v2.0.0",
                    creator_id=1,
                    assignee_id=0,
                    last_changer_id=1
                )
            ]
            session.add_all(demo_bugs)
            await session.commit()
            print(f"✅ Seeded {len(demo_bugs)} demo bugs.")
        else:
            await session.commit()
            print("ℹ️  Bugs already exist, skipping demo bug creation.")

async def main():
    parser = argparse.ArgumentParser(description="BugTracer Database Management")
    parser.add_argument("--reset", action="store_true", help="Drop all tables and recreate database")
    parser.add_argument("--seed-demo", action="store_true", help="Populate sample demo data")
    args = parser.parse_args()

    print(f"🔧 Target Database: {settings.effective_database_url}")

    if args.reset:
        await reset_database()

    print("🚀 Initializing database schema...")
    await init_db()
    print("✅ Database schema initialized successfully.")

    if args.seed_demo:
        await seed_demo_data()

    print("\n✨ Ready to start! Run: python run.py")

if __name__ == "__main__":
    asyncio.run(main())
