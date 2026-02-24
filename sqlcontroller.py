from typing import List,Optional
import sqlite3
from structs import *
class UserDatabase:
    """User 类的 SQLite3 数据库管理器"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 支持字典访问
        self._create_table()
    
    def _create_table(self):
        """创建用户表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL DEFAULT '',
                user_displayname TEXT NOT NULL DEFAULT '',
                user_remark TEXT NOT NULL DEFAULT ''
            )
        ''')
        self.conn.commit()
    
    def save_user(self, user: User) -> bool:
        """保存单个用户（插入或更新）"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, user_name, user_displayname, user_remark)
                VALUES (?, ?, ?, ?)
            ''', (user.user_id, user.user_name, 
                  user.user_displayname, user.user_remark))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存用户失败: {e}")
            return False
    def get_user_by_name(self, user_name: str) -> List[User]:
        """根据用户名获取用户列表（返回 User 数组）"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_name = ?', (user_name,))
        rows = cursor.fetchall()
        return [User.from_dict(dict(row)) for row in rows]
    def save_users(self, users: List[User]) -> int:
        """批量保存用户数组"""
        cursor = self.conn.cursor()
        try:
            data = [(u.user_id, u.user_name, 
                    u.user_displayname, u.user_remark) for u in users]
            cursor.executemany('''
                INSERT OR REPLACE INTO users 
                (user_id, user_name, user_displayname, user_remark)
                VALUES (?, ?, ?, ?)
            ''', data)
            self.conn.commit()
            return len(data)
        except sqlite3.Error as e:
            print(f"批量保存失败: {e}")
            return 0
    
    def get_user(self, user_id: str) -> Optional[User]:
        """根据 ID 获取单个用户"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return User.from_dict(dict(row)) if row else None
    
    def get_all_users(self) -> List[User]:
        """获取所有用户（返回 User 数组）"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        return [User.from_dict(dict(row)) for row in rows]
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"删除失败: {e}")
            return False
    
    def delete_all(self):
        """清空所有用户"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM users')
        self.conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class GroupDatabase:
    """Group 类的 SQLite3 数据库管理器"""
    
    def __init__(self, db_path: str = "groups.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()
    
    def _create_table(self):
        """创建群组表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT PRIMARY KEY,
                group_name TEXT NOT NULL DEFAULT ''
            )
        ''')
        self.conn.commit()
    
    def save_group(self, group: Group) -> bool:
        """保存单个群组"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO groups (group_id, group_name)
                VALUES (?, ?)
            ''', (group.group_id, group.group_name))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存群组失败: {e}")
            return False
    def delete_all(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM groups')
        self.conn.commit()
    
    def save_groups(self, groups: List[Group]) -> int:
        """批量保存群组数组"""
        cursor = self.conn.cursor()
        try:
            data = [(g.group_id, g.group_name) for g in groups]
            cursor.executemany('''
                INSERT OR REPLACE INTO groups (group_id, group_name)
                VALUES (?, ?)
            ''', data)
            self.conn.commit()
            return len(data)
        except sqlite3.Error as e:
            print(f"批量保存失败: {e}")
            return 0
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """根据 ID 获取单个群组"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE group_id = ?', (group_id,))
        row = cursor.fetchone()
        return Group.from_dict(dict(row)) if row else None
    
    def get_all_groups(self) -> List[Group]:
        """获取所有群组"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM groups')
        rows = cursor.fetchall()
        return [Group.from_dict(dict(row)) for row in rows]
    
    def delete_group(self, group_id: str) -> bool:
        """删除群组"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM groups WHERE group_id = ?', (group_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"删除失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
class GroupMemberDatabase:
    def __init__(self, db_path: str = "group_members.db"):
        self.db_path = db_path
        self._init_table()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_table(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS group_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    nickname TEXT DEFAULT '',
                    card TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_group_id 
                ON group_members(group_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON group_members(user_id)
            """)
    
    def insert(self, member: GroupMember) -> int:
        """插入单个成员，返回新记录的 id"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO group_members 
                (group_id, user_id, nickname, card)
                VALUES (?, ?, ?, ?)
            """, (member.group_id, member.user_id, 
                  member.nickname, member.card))
            return cursor.lastrowid #type: ignore
    
    def insert_many(self, members: List[GroupMember]) -> int:
        """批量插入成员，返回插入的数量"""
        with self.get_connection() as conn:
            data = [(m.group_id, m.user_id, m.nickname, m.card) 
                    for m in members]
            cursor = conn.executemany("""
                INSERT INTO group_members 
                (group_id, user_id, nickname, card)
                VALUES (?, ?, ?, ?)
            """, data)
            return cursor.rowcount
    
    def get_by_group(self, group_id: str) -> List[GroupMember]:
        """根据群组ID获取所有成员"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, group_id, user_id, nickname, card 
                FROM group_members 
                WHERE group_id = ?
                ORDER BY id DESC
            """, (group_id,))
            return [GroupMember(**dict(row)) for row in cursor.fetchall()]
    
    def get_by_user(self, user_id: str) -> List[GroupMember]:
        """根据用户ID获取所有记录"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, group_id, user_id, nickname, card 
                FROM group_members 
                WHERE user_id = ?
                ORDER BY id DESC
            """, (user_id,))
            return [GroupMember(**dict(row)) for row in cursor.fetchall()]
    
    def get_one(self, record_id: int) -> Optional[GroupMember]:
        """根据记录 ID 获取单条记录"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, group_id, user_id, nickname, card 
                FROM group_members 
                WHERE id = ?
            """, (record_id,))
            row = cursor.fetchone()
            return GroupMember(**dict(row)) if row else None
    
    def get_latest(self, group_id: str, user_id: str) -> Optional[GroupMember]:
        """获取某用户在某群组的最新记录"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, group_id, user_id, nickname, card 
                FROM group_members 
                WHERE group_id = ? AND user_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (group_id, user_id))
            row = cursor.fetchone()
            return GroupMember(**dict(row)) if row else None
    
    def update(self, record_id: int, member: GroupMember) -> bool:
        """根据记录 ID 更新成员信息"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                UPDATE group_members 
                SET nickname = ?, card = ?
                WHERE id = ?
            """, (member.nickname, member.card, record_id))
            return cursor.rowcount > 0
    
    def delete(self, record_id: int) -> bool:
        """根据记录 ID 删除单条记录"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM group_members 
                WHERE id = ?
            """, (record_id,))
            return cursor.rowcount > 0
    
    def delete_by_group(self, group_id: str) -> int:
        """删除整个群组的所有记录"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM group_members 
                WHERE group_id = ?
            """, (group_id,))
            return cursor.rowcount
    
    def delete_by_user(self, user_id: str) -> int:
        """删除某用户的所有记录"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM group_members 
                WHERE user_id = ?
            """, (user_id,))
            return cursor.rowcount
    
    def delete_one(self, group_id: str, user_id: str) -> bool:
        """删除某用户在某群组的一条记录（最新的一条）"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM group_members 
                WHERE id = (
                    SELECT id FROM group_members 
                    WHERE group_id = ? AND user_id = ? 
                    ORDER BY id DESC LIMIT 1
                )
            """, (group_id, user_id))
            return cursor.rowcount > 0
    
    def delete_all(self) -> int:
        """删除所有记录，返回删除的数量"""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM group_members")
            return cursor.rowcount
    
    def count(self, group_id: str) -> int:
        """获取群组的记录总数"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM group_members 
                WHERE group_id = ?
            """, (group_id,))
            return cursor.fetchone()[0]
    
    def count_all(self) -> int:
        """获取总记录数"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM group_members")
            return cursor.fetchone()[0]
    
    def count_unique_users(self, group_id: str) -> int:
        """获取群组的去重用户数"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT user_id) FROM group_members 
                WHERE group_id = ?
            """, (group_id,))
            return cursor.fetchone()[0]
    
    def get_all(self) -> List[GroupMember]:
        """获取所有记录"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, group_id, user_id, nickname, card 
                FROM group_members
                ORDER BY id DESC
            """)
            return [GroupMember(**dict(row)) for row in cursor.fetchall()]
    
    def exists(self) -> bool:
        """检查是否有任何记录"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT EXISTS(SELECT 1 FROM group_members LIMIT 1)
            """)
            return cursor.fetchone()[0] == 1

class PrivateMessageDB:
    def __init__(self, db_path: str = "private_messages.db"):
        self.db_path = db_path
        self._init_table()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_table(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS private_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_type TEXT NOT NULL,
                    message_id TEXT NOT NULL UNIQUE,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    raw_message TEXT,
                    create_time TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON private_messages(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_create_time ON private_messages(create_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_message_type ON private_messages(message_type)")
    
    def insert(self, msg: PrivateMessage) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO private_messages 
                (message_type, message_id, user_id, message, raw_message, create_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (msg.message_type, msg.message_id, msg.user_id, 
                  msg.message, msg.raw_message, msg.create_time))
            return cursor.lastrowid #type:ignore
    
    def insert_many(self, messages: List[PrivateMessage]) -> int:
        with self.get_connection() as conn:
            data = [(m.message_type, m.message_id, m.user_id, 
                     m.message, m.raw_message, m.create_time) 
                    for m in messages]
            cursor = conn.executemany("""
                INSERT OR REPLACE INTO private_messages 
                (message_type, message_id, user_id, message, raw_message, create_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)
            return cursor.rowcount
    
    # ==================== 新增方法 ====================
    
    def get_group_messages(self, limit: int = 100, offset: int = 0) -> List[PrivateMessage]:
        """获取所有群组消息列表"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, message_type, message_id, user_id, message, raw_message, create_time
                FROM private_messages 
                WHERE message_type = 'group'
                ORDER BY create_time DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            return [PrivateMessage(**dict(row)) for row in cursor.fetchall()]
    
    def get_private_messages(self, limit: int = 100, offset: int = 0) -> List[PrivateMessage]:
        """获取所有私聊消息列表"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, message_type, message_id, user_id, message, raw_message, create_time
                FROM private_messages 
                WHERE message_type = 'private'
                ORDER BY create_time DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            return [PrivateMessage(**dict(row)) for row in cursor.fetchall()]
    
    # ==================== 原有方法 ====================
    
    def get_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> List[PrivateMessage]:
        """获取某用户的所有消息（分页）"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, message_type, message_id, user_id, message, raw_message, create_time
                FROM private_messages 
                WHERE user_id = ?
                ORDER BY create_time DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            return [PrivateMessage(**dict(row)) for row in cursor.fetchall()]
    
    def get_by_message_id(self, message_id: str) -> Optional[PrivateMessage]:
        """根据消息 ID 获取消息"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, message_type, message_id, user_id, message, raw_message, create_time
                FROM private_messages 
                WHERE message_id = ?
            """, (message_id,))
            row = cursor.fetchone()
            return PrivateMessage(**dict(row)) if row else None
    
    def get_by_type(self, message_type: str, limit: int = 100) -> List[PrivateMessage]:
        """根据消息类型获取消息"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, message_type, message_id, user_id, message, raw_message, create_time
                FROM private_messages 
                WHERE message_type = ?
                ORDER BY create_time DESC
                LIMIT ?
            """, (message_type, limit))
            return [PrivateMessage(**dict(row)) for row in cursor.fetchall()]
    
    def delete(self, message_id: str) -> bool:
        """根据消息 ID 删除消息"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM private_messages 
                WHERE message_id = ?
            """, (message_id,))
            return cursor.rowcount > 0
    
    def delete_by_user(self, user_id: str) -> int:
        """删除某用户的所有消息"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM private_messages 
                WHERE user_id = ?
            """, (user_id,))
            return cursor.rowcount
    
    def delete_all(self) -> int:
        """删除所有消息"""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM private_messages")
            return cursor.rowcount
    
    def count(self, user_id: Optional[str] = None) -> int:
        """获取消息总数"""
        with self.get_connection() as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM private_messages WHERE user_id = ?
                """, (user_id,))
            else:
                cursor = conn.execute("SELECT COUNT(*) FROM private_messages")
            return cursor.fetchone()[0]
    
    def count_by_type(self, message_type: str) -> int:
        """获取某类型的消息数"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM private_messages WHERE message_type = ?
            """, (message_type,))
            return cursor.fetchone()[0]
    
    def count_group(self) -> int:
        """获取群组消息总数"""
        return self.count_by_type('group')
    
    def count_private(self) -> int:
        """获取私聊消息总数"""
        return self.count_by_type('private')
    
    def get_all(self, limit: int = 1000, offset: int = 0) -> List[PrivateMessage]:
        """获取所有消息（分页）"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, message_type, message_id, user_id, message, raw_message, create_time
                FROM private_messages
                ORDER BY create_time DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            return [PrivateMessage(**dict(row)) for row in cursor.fetchall()]