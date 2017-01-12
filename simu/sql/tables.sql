drop database fund;
create database fund;
use fund;
CREATE TABLE CityInfo(
  id INT(11) NOT NULL AUTO_INCREMENT,
  city VARCHAR(20) NOT NULL,
  PRIMARY KEY (id)
)DEFAULT CHAR SET = utf8;

CREATE TABLE AdvisorInfo(
  id INT(11) NOT NULL AUTO_INCREMENT,
  advisor_id VARCHAR(20) NOT NULL,
  advisor_short_name VARCHAR(100) NOT NULL,
  PRIMARY KEY (id)
)DEFAULT CHAR SET = utf8;

CREATE TABLE FundInfo(
  id INT(11) NOT NULL AUTO_INCREMENT,
  fund_id VARCHAR(20) NOT NULL,
  fund_short_name VARCHAR(100) NOT NULL,
  initial_date DATE,
  register_number VARCHAR(20),
  advisor_id int(11),
  CONSTRAINT FOREIGN KEY (advisor_id) REFERENCES AdvisorInfo(id),
  city INT(11),
  CONSTRAINT FOREIGN KEY (city) REFERENCES CityInfo(id),
  managers_id VARCHAR(100),
  managers_name VARCHAR(100),
  change_col int(11),
  fund_status int(11),
  fund_type int(11),
  inception_year int(11),
  initial_unit_value double,
  profession_background int(11),
  strategy int(11),
  umbrella_fund int(11),
  inception_date date,
  liquidate_date date,
  status_end_date date,
  blackout_period varchar(20),
  open_day varchar(20),
  purchase_starting_point double,
  add_purchase_point double,
  purchase_fee double,
  redemption_fee double,
  warning_level double,
  stop_loss_level double,
  register_code varchar(20),
  initial_amount double,
  term varchar(20),
  is_tier bool,
  is_umbrella bool,
  production_type varchar(20),
  performance_fee double,
  fund_manager varchar(20),
  manage_fee double,
  trustee varchar(20),
  stock_broker varchar(20),
  future_broker varchar(20),
  disclosure_mark varchar(20),
  PRIMARY KEY (id)
)DEFAULT CHAR SET = utf8;

CREATE TABLE NetValue(
  fund_id int(11) NOT NULL,
  CONSTRAINT FOREIGN KEY (fund_id) REFERENCES FundInfo(id),
  date date NOT NULL,
  value double NOT NULL
)DEFAULT CHAR SET = utf8;

CREATE TABLE ErrorFund_Net(
  id int(11) NOT NULL AUTO_INCREMENT,
  fund_id int(11) NOT NULL,
  CONSTRAINT FOREIGN KEY (fund_id) REFERENCES FundInfo(id),
  PRIMARY KEY(id)
)DEFAULT CHAR SET = utf8;

CREATE TABLE ErrorFund_FundInfo(
  id int(11) NOT NULL AUTO_INCREMENT,
  fund_id int(11) NOT NULL,
  CONSTRAINT FOREIGN KEY (fund_id) REFERENCES FundInfo(id),
  PRIMARY KEY (id)
)DEFAULT CHAR SET = utf8;