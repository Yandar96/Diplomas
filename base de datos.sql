create database diplomas;
use diplomas;

create table persona(
identificacion int primary key,
nombreCompleto varchar(100),
pago varchar(10) 
);

create table curso(
codigo int primary key,
nombre varchar(100),
diploma varchar(255)
);

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) not null,
    rol enum('admin','usuario')
);

INSERT INTO usuarios (username, password, rol) VALUES ('yandar', 'scrypt:32768:8:1$qa1mwaOYqJDg3xrx$0baa02286bee828b21805bb35ded7c4c620c81f18de13122c38fd3a065a1ad97fb0d4a0af4cd7616a6e59cc476cc6e112ff6d86073dd8410fee793f51451a468', 'admin');


create table detallePersona(
codigo int primary key auto_increment,
idPersona int,
codCurso int,
foreign key (idPersona) references persona(identificacion),
foreign key (codCurso) references curso(codigo)
);