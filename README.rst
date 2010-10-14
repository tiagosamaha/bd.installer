Biblioteca Digital
==================

Biblioteca Digital pode ser instalada a partir deste módulo, que contém o
buildout e scripts para instalação de dependências.
Esta é uma instalação para deploy (produção).

Pré-Requisitos
==============

A solução da Biblioteca Digital depende do sistema operacional Debian 5, com
respositório `unstable` habilitado (equivalente ao Debian Squeeze).
Para habilitar o repositório `unstable` certifique-se que o conteúdo do
arquivo `/etc/apt/source.list` seja o listado abaixo:

::
    
    deb http://ftp.br.debian.org/debian/ sid main contrib non-free
    deb-src http://ftp.br.debian.org/debian/ sid main contrib non-free

    deb ftp://ftp.debian-multimedia.org sid main non-free
    deb-src ftp://ftp.debian-multimedia.org sid main non-free

    deb http://security.debian.org/ lenny/updates main
    deb-src http://security.debian.org/ lenny/updates main

    deb http://volatile.debian.org/debian-volatile lenny/volatile main
    deb-src http://volatile.debian.org/debian-volatile lenny/volatile main

Atualize todo o sistema com as atualizações disponíveis neste repositório,
através do comando abaixo.

::

    apt-get update && apt-get dist-upgrade
