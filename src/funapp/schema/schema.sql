-- 基础表：无外键依赖
CREATE TABLE t_user (
    id              BIGINT       NULL AUTO_INCREMENT COMMENT '主键ID，自增长',
    created_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    status          INT          NULL DEFAULT 1 COMMENT '状态：1-下架，2-在架，3-删除，4-过期',
    username        VARCHAR(50)  NULL COMMENT '用户名，用于登录',
    password        VARCHAR(100) NULL COMMENT '密码，存储加密后的密码',
    mobile          VARCHAR(20)  NULL COMMENT '手机号码',
    email           VARCHAR(100) NULL COMMENT '电子邮箱地址',
    nickname        VARCHAR(50)  NULL COMMENT '用户昵称，用于展示',
    avatar_url      VARCHAR(255) NULL COMMENT '用户头像URL',
    user_level      INT          NULL DEFAULT 1 COMMENT '用户等级',
    last_login_time TIMESTAMP    NULL COMMENT '最后登录时间',
    PRIMARY KEY (id),
    UNIQUE KEY UK_user_username (username),
    UNIQUE KEY UK_user_mobile (mobile),
    UNIQUE KEY UK_user_email (email)
) COMMENT '用户表：存储用户基本信息';

CREATE TABLE t_theme (
    id              BIGINT       NULL AUTO_INCREMENT COMMENT '主键ID，自增长',
    created_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    status          INT          NULL DEFAULT 1 COMMENT '状态：1-下架，2-在架，3-删除，4-过期',
    name            VARCHAR(50)  NULL COMMENT '主题名称，如"春节"、"国庆"等',
    description     TEXT         NULL COMMENT '主题详细描述信息',
    icon_url        VARCHAR(255) NULL COMMENT '主题图标资源链接',
    PRIMARY KEY (id),
    UNIQUE KEY UK_theme_name (name)
) COMMENT '主题表：存储所有活动主题基础信息';

CREATE TABLE t_game (
    id              BIGINT       NULL AUTO_INCREMENT COMMENT '主键ID，自增长',
    created_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    status          INT          NULL DEFAULT 1 COMMENT '状态：1-下架，2-在架，3-删除，4-过期',
    name            VARCHAR(100) NULL COMMENT '游戏名称，如"2048经典版"',
    game_type       VARCHAR(50)  NULL COMMENT '游戏类型标识，如"2048"、"sudoku"等',
    description     TEXT         NULL COMMENT '游戏简介，用于展示',
    rules           TEXT         NULL COMMENT '游戏规则详细说明',
    default_config  JSON         NULL COMMENT '默认游戏配置参数，JSON格式',
    PRIMARY KEY (id),
    UNIQUE KEY UK_game_type (game_type)
) COMMENT '游戏表：存储游戏的基本信息与规则';

-- 第二层依赖：依赖于基础表
CREATE TABLE t_campaign (
    id              BIGINT       NULL AUTO_INCREMENT COMMENT '主键ID，自增长',
    created_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    status          INT          NULL DEFAULT 1 COMMENT '状态：1-下架，2-在架，3-删除，4-过期',
    name            VARCHAR(100) NULL COMMENT '活动名称，用于展示',
    description     TEXT         NULL COMMENT '活动详细介绍与规则说明',
    start_time      TIMESTAMP    NULL COMMENT '活动开始时间，用于自动上架',
    end_time        TIMESTAMP    NULL COMMENT '活动结束时间，用于自动下架',
    theme_id        BIGINT       NULL COMMENT '主题ID，对应t_theme表的主键',
    max_level_count INT          NULL DEFAULT 1 COMMENT '活动最大关卡数，用于计算进度百分比',
    PRIMARY KEY (id),
    UNIQUE KEY UK_campaign_name (name)
) COMMENT '活动表：存储活动的基本信息与配置';

CREATE TABLE t_game_instance (
    id              BIGINT       NULL AUTO_INCREMENT COMMENT '主键ID，自增长',
    created_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    status          INT          NULL DEFAULT 1 COMMENT '状态：1-下架，2-在架，3-删除，4-过期',
    name            VARCHAR(100) NULL COMMENT '实例名称，如"简单模式"、"困难模式"',
    diff_level      INT          NULL DEFAULT 4 COMMENT '难度等级：1-3简单，4-6中等，7-9困难，10地狱模式',
    game_id         BIGINT       NULL COMMENT '关联的游戏ID，对应t_game表',
    config          JSON         NULL COMMENT '游戏实例特定配置，如难度、目标分数等',
    time_limit      INT          NULL COMMENT '时间限制(秒)，0表示无限制',
    PRIMARY KEY (id),
    UNIQUE KEY UK_game_instance_name_game (name, game_id)
) COMMENT '游戏实例表：基于游戏定义的具体实例配置';

-- 第三层依赖：依赖于前两层表
CREATE TABLE t_campaign_level (
    id              BIGINT       NULL AUTO_INCREMENT COMMENT '主键ID，自增长',
    created_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    status          INT          NULL DEFAULT 1 COMMENT '状态：1-下架，2-在架，3-删除，4-过期',
    name            VARCHAR(100) NULL COMMENT '关卡名称，用于界面展示',
    campaign_id     BIGINT       NULL COMMENT '所属活动ID，关联t_campaign表的主键',
    level_number    INT          NULL COMMENT '关卡序号，决定显示顺序',
    game_id         BIGINT       NULL COMMENT '关联的游戏ID，对应t_game表',
    game_instance_id BIGINT      NULL COMMENT '关联的游戏实例ID，指定关卡使用的游戏配置',
    reward_config   JSON         NULL COMMENT '奖励配置，包含奖励类型、数量等JSON格式数据',
    PRIMARY KEY (id),
    UNIQUE KEY UK_campaign_level_number (campaign_id, level_number)
) COMMENT '活动关卡表：定义活动中的各个游戏关卡';

-- 最终层依赖：依赖于所有前面的表
CREATE TABLE t_user_game_record (
    id              BIGINT       NULL AUTO_INCREMENT COMMENT '主键ID，自增长',
    created_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at      TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    status          INT          NULL DEFAULT 1 COMMENT '状态：1-下架，2-在架，3-删除，4-过期',
    user_id         BIGINT       NOT NULL COMMENT '用户ID，标识游戏参与者',
    game_id         BIGINT       NULL COMMENT '游戏ID，对应t_game表',
    game_instance_id BIGINT      NOT NULL COMMENT '游戏实例ID，关联t_game_instance表',
    theme_id        BIGINT       NULL COMMENT '主题ID，对应t_theme表',
    campaign_id     BIGINT       NULL COMMENT '活动ID，对应t_campaign表',
    campaign_level_id BIGINT     NULL COMMENT '活动关卡ID，为空表示非活动游戏',
    score           INT          NULL COMMENT '用户获得的游戏分数',
    start_time      TIMESTAMP    NULL COMMENT '闯关开始时间',
    completed_at    TIMESTAMP    NULL COMMENT '游戏完成时间戳',
    is_success      BOOLEAN      NULL DEFAULT FALSE COMMENT '是否闯关成功：true-成功，false-失败',
    PRIMARY KEY (id)
) COMMENT '用户游戏记录表：记录用户参与游戏的成绩数据';

-- 用户活动闯关进度表：依赖于用户表和活动表
CREATE TABLE t_user_campaign_progress (
    id                  BIGINT       NULL AUTO_INCREMENT COMMENT '主键ID，自增长',
    created_at          TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at          TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    status              INT          NULL DEFAULT 1 COMMENT '状态：1-下架，2-在架，3-删除，4-过期',
    user_id             BIGINT       NOT NULL COMMENT '用户ID，对应t_user表',
    campaign_id         BIGINT       NOT NULL COMMENT '活动ID，对应t_campaign表',
    theme_id            BIGINT       NULL COMMENT '主题ID，对应t_theme表',
    current_level_num   INT          NULL DEFAULT 1 COMMENT '当前关卡序号',
    is_completed        BOOLEAN      NULL DEFAULT FALSE COMMENT '是否完成全部关卡：true-已完成，false-未完成',
    completed_at        TIMESTAMP    NULL COMMENT '活动完成时间',
    last_play_time      TIMESTAMP    NULL COMMENT '最后一次游玩时间',
    PRIMARY KEY (id),
    UNIQUE KEY UK_user_campaign (user_id, campaign_id)
) COMMENT '用户活动进度表：记录用户在每个活动中的闯关进度';

-- 添加外键约束
ALTER TABLE t_campaign
    ADD CONSTRAINT FK_theme_TO_campaign
    FOREIGN KEY (theme_id)
    REFERENCES t_theme (id);

ALTER TABLE t_game_instance
    ADD CONSTRAINT FK_game_TO_game_instance
    FOREIGN KEY (game_id)
    REFERENCES t_game (id);

ALTER TABLE t_campaign_level
    ADD CONSTRAINT FK_campaign_TO_campaign_level
    FOREIGN KEY (campaign_id)
    REFERENCES t_campaign (id);

ALTER TABLE t_campaign_level
    ADD CONSTRAINT FK_game_instance_TO_campaign_level
    FOREIGN KEY (game_instance_id)
    REFERENCES t_game_instance (id);

ALTER TABLE t_user_game_record
    ADD CONSTRAINT FK_user_TO_user_game_record
    FOREIGN KEY (user_id)
    REFERENCES t_user (id);

ALTER TABLE t_user_game_record
    ADD CONSTRAINT FK_game_instance_TO_user_game_record
    FOREIGN KEY (game_instance_id)
    REFERENCES t_game_instance (id);

ALTER TABLE t_user_game_record
    ADD CONSTRAINT FK_campaign_level_TO_user_game_record
    FOREIGN KEY (campaign_level_id)
    REFERENCES t_campaign_level (id);

ALTER TABLE t_user_campaign_progress
    ADD CONSTRAINT FK_user_TO_user_campaign_progress
    FOREIGN KEY (user_id)
    REFERENCES t_user (id);

ALTER TABLE t_user_campaign_progress
    ADD CONSTRAINT FK_campaign_TO_user_campaign_progress
    FOREIGN KEY (campaign_id)
    REFERENCES t_campaign (id);

-- 添加索引
CREATE INDEX idx_user_username ON t_user (username ASC);
CREATE INDEX idx_user_mobile ON t_user (mobile ASC);
CREATE INDEX idx_user_email ON t_user (email ASC);
CREATE INDEX idx_user_status ON t_user (status ASC);

CREATE INDEX idx_theme_status ON t_theme (status ASC);
CREATE INDEX idx_theme_name ON t_theme (name ASC);

CREATE INDEX idx_campaign_status ON t_campaign (status ASC);
CREATE INDEX idx_campaign_time ON t_campaign (start_time ASC, end_time ASC);
CREATE INDEX idx_campaign_theme ON t_campaign (theme_id ASC);

CREATE INDEX idx_game_type ON t_game (game_type ASC);
CREATE INDEX idx_game_status ON t_game (status ASC);

CREATE INDEX idx_game_inst_game ON t_game_instance (game_id ASC);
CREATE INDEX idx_game_inst_status ON t_game_instance (status ASC);
CREATE INDEX idx_game_inst_diff ON t_game_instance (diff_level ASC);

CREATE INDEX idx_camp_level_campaign ON t_campaign_level (campaign_id ASC);
CREATE INDEX idx_camp_level_game ON t_campaign_level (game_instance_id ASC);
CREATE INDEX idx_camp_level_status ON t_campaign_level (status ASC);
CREATE INDEX idx_camp_level_number ON t_campaign_level (level_number ASC);
CREATE INDEX idx_camp_level_game_id ON t_campaign_level (game_id ASC);

CREATE INDEX idx_game_record_user ON t_user_game_record (user_id ASC);
CREATE INDEX idx_game_record_instance ON t_user_game_record (game_instance_id ASC);
CREATE INDEX idx_game_record_level ON t_user_game_record (campaign_level_id ASC);
CREATE INDEX idx_game_record_score ON t_user_game_record (score DESC);
CREATE INDEX idx_game_record_completed ON t_user_game_record (completed_at ASC);
CREATE INDEX idx_game_record_game ON t_user_game_record (game_id ASC);
CREATE INDEX idx_game_record_theme ON t_user_game_record (theme_id ASC);
CREATE INDEX idx_game_record_campaign ON t_user_game_record (campaign_id ASC);

CREATE INDEX idx_user_progress_user ON t_user_campaign_progress (user_id ASC);
CREATE INDEX idx_user_progress_campaign ON t_user_campaign_progress (campaign_id ASC);
CREATE INDEX idx_user_progress_level ON t_user_campaign_progress (current_level_num ASC);
CREATE INDEX idx_user_progress_completed ON t_user_campaign_progress (is_completed ASC);
CREATE INDEX idx_user_progress_theme ON t_user_campaign_progress (theme_id ASC);
