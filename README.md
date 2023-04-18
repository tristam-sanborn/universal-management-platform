# Universal-Management-Platform
Authors: Tristam Sanborn, John Kalogeropoulos, Connor Adams, Juan Moran Lopez

Copyright 2023 Universal Management Platform

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Build Process:

Run the follow SQL script in MySQL Workbench:

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema ump_database
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema ump_database
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ump_database` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `ump_database` ;

-- -----------------------------------------------------
-- Table `ump_database`.`employees`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ump_database`.`employees` (
  `uid` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NULL DEFAULT NULL,
  `password` VARCHAR(255) NULL DEFAULT NULL,
  `permission` INT NULL DEFAULT NULL,
  `email` VARCHAR(45) NULL DEFAULT NULL,
  `phone` VARCHAR(45) NULL DEFAULT NULL,
  `firstname` VARCHAR(45) NULL DEFAULT NULL,
  `lastname` VARCHAR(45) NULL DEFAULT NULL,
  `middleinitial` VARCHAR(45) NULL DEFAULT NULL,
  `address` VARCHAR(45) NULL DEFAULT NULL,
  `role` VARCHAR(45) NULL DEFAULT NULL,
  `manager` VARCHAR(45) NULL DEFAULT NULL,
  `company_name` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`uid`))
ENGINE = InnoDB
AUTO_INCREMENT = 1030
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `ump_database`.`assetlist`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ump_database`.`assetlist` (
  `assetid` INT NOT NULL AUTO_INCREMENT,
  `assetOwner` INT NULL DEFAULT NULL,
  `assetName` VARCHAR(45) NULL DEFAULT NULL,
  `location` VARCHAR(45) NULL DEFAULT NULL,
  `assetCount` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`assetid`),
  INDEX `assetOwner_idx` (`assetOwner` ASC) VISIBLE,
  CONSTRAINT `assetOwner`
    FOREIGN KEY (`assetOwner`)
    REFERENCES `ump_database`.`employees` (`uid`))
ENGINE = InnoDB
AUTO_INCREMENT = 100001
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

Create the Login account and first admin account with the following command in a SQL Query:
Note: The admin account you will have to use to first login is username: 'Admin' password: 'password'.

create user 'loginSvcMgr'@'localhost' identified by '18ATBeK.9Zjleo\}sS]N2DMQrdc1WI&J-(;X/,yL!vD3T8P$2';
grant select, alter
on ump_database
to 'loginSvcMgr';

create user 'admin' identified by 'password';
grant select, alter, create, delete, insert
on ump_databse
to 'admin' with grant option;
INSERT INTO `ump_database`.`employees` (`uid`, `username`, `password`, `permission`, `email`, `phone`, `firstname`, `lastname`, `middleinitial`, `address`, `role`, `manager`, `company_name`) VALUES ('1000', 'admin', 'password', '0', 'admin@ump.com', '123-456-7890', 'Admin', 'Account', 'A', '123 Road Road', 'admin', 'none', 'ump');


In the IDE that you have brought the code into, go into the terminal and run the command 'python appV1_04.py' and click the ip adress that is says "Running on".
This will bring you to our login webpage where you can start using UMP.

If you get errors, there are some dependencies you may have to run in the terminal. These are listed below. 
pip install flask, pip install mysql.connector, pip install os, pip install json, pip install datetime, pip install werkzeug.utils.
