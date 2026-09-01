from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from .base import Base

Base = declarative_base()

# 创建数据库连接
engine = create_engine("mysql+pymysql://username:password@localhost/dbname")


# 创建所有表
def create_tables():
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


from sqlalchemy import JSON, BigInteger, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .base import Base


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


from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


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


from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


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


from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


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
