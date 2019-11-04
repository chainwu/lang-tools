create dabasase corpus CHARACTER SET utf8 COLLATE utf8_general_ci;
use corpus;
create table file_table (
    file_id int unsigned not null unique auto_increment,
    txtgrid varchar(256),
    wav varchar(256),
    primary key (file_id)
);

create table textgrid_table (
    textgrid_id int unsigned not null unique auto_increment,
    file_id int,
    total_tier int,
    start_time DECIMAL(10,15),
    end_time DECIMAL(10,15),
    primary key (textgrid_id)
);

create table tier_table(
    tier_id int unsigned not null unique auto_increment,
    textgrid_id int,
    seq_id int,
    tier_name varchar(256),
    tier_type,
    start_time DECIMAL(10,15),
    end_time DECIMAL(10,15),
    primary key (tier_id)
);

create table annotation(
    ann_id int unsigned not null unique auto_increment,
    text varchar(4096),
    tier_id int,
    seq_id int unsigned,
    start_time DECIMAL(10,15),
    end_time DECIMAL(10,15),
    primary key (ann_id)
);
