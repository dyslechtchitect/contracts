-- mydb.contracts definition

CREATE TABLE `contracts` (
  `id` varbinary(16) NOT NULL,
  `title` varchar(256) DEFAULT NULL,
  `body` json DEFAULT NULL,
  `date_created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `date_updated` varchar(45) DEFAULT 'CURRENT_TIMESTAMP',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- mydb.users definition

CREATE TABLE `users` (
  `id` varbinary(16) NOT NULL,
  `userId` varbinary(16) NOT NULL,
  `date_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `date_created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- mydb.contracts_to_users definition

CREATE TABLE `contracts_to_users` (
  `id` varbinary(16) NOT NULL,
  `is_creator` tinyint(1) DEFAULT NULL,
  `is_editor` tinyint(1) DEFAULT NULL,
  `is_party` tinyint(1) DEFAULT NULL,
  `date_created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `date_updated` timestamp NULL DEFAULT NULL,
  `signed` tinyint(1) NOT NULL DEFAULT '0',
  `date_expires` timestamp NULL DEFAULT NULL,
  `date_starts` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_contracts_to_users_1` FOREIGN KEY (`id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_contracts_to_users_2` FOREIGN KEY (`id`) REFERENCES `contracts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;