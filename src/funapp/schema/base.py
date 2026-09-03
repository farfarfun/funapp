from funsecret import read_secret
from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# 数据库连接串通过 funsecret 下发，不硬编码真实凭据；未配置时回落到本地开发默认值
_db_url = read_secret(
    "funapp",
    "mysql",
    "url",
    value="mysql+pymysql://username:password@localhost/dbname",
)
engine = create_engine(_db_url)


def create_tables():
    """创建所有表。"""
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = "t_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    username = Column(String(50), unique=True)
    password = Column(String(100))
    mobile = Column(String(20), unique=True)
    email = Column(String(100), unique=True)
    nickname = Column(String(50))
    avatar_url = Column(String(255))
    user_level = Column(Integer, default=1)
    last_login_time = Column(DateTime)


class Theme(Base):
    __tablename__ = "t_theme"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(50), unique=True)
    description = Column(Text)
    icon_url = Column(String(255))


class Game(Base):
    __tablename__ = "t_game"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(100))
    game_type = Column(String(50), unique=True)
    description = Column(Text)
    rules = Column(Text)
    default_config = Column(JSON)


class Campaign(Base):
    __tablename__ = "t_campaign"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(100), unique=True)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    theme_id = Column(BigInteger, ForeignKey("t_theme.id"))
    max_level_count = Column(Integer, default=1)

    theme = relationship("Theme")


class GameInstance(Base):
    __tablename__ = "t_game_instance"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(100))
    diff_level = Column(Integer, default=4)
    game_id = Column(BigInteger, ForeignKey("t_game.id"))
    config = Column(JSON)
    time_limit = Column(Integer)

    game = relationship("Game")


class CampaignLevel(Base):
    __tablename__ = "t_campaign_level"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    status = Column(Integer, default=1)
    name = Column(String(100))
    campaign_id = Column(BigInteger, ForeignKey("t_campaign.id"))
    level_number = Column(Integer)
    game_id = Column(BigInteger, ForeignKey("t_game.id"))
    game_instance_id = Column(BigInteger, ForeignKey("t_game_instance.id"))
    reward_config = Column(JSON)

    campaign = relationship("Campaign")
    game = relationship("Game")
    game_instance = relationship("GameInstance")
