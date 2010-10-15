Biblioteca Digital
==================

Biblioteca Digital pode ser instalada a partir deste m�dulo, que cont�m o
buildout e scripts para instala��o de depend�ncias.
Esta � uma instala��o para deploy (produ��o).

Pr�-Requisitos
==============

A solu��o da Biblioteca Digital depende do sistema operacional Debian 5, com
resposit�rio `unstable` habilitado (equivalente ao Debian Squeeze).
Para habilitar o reposit�rio `unstable` certifique-se que o conte�do do
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

Atualize todo o sistema com as atualiza��es dispon�veis neste reposit�rio,
atrav�s do comando abaixo.

::

    servidor:~# apt-get update && apt-get dist-upgrade

Ap�s toda atualiza��o do sistema, instale dois aplicativos necess�rios para
pr�-instala��o da solu��o.

::

    servidor:~# apt-get install make subversion

Instala��o
==========

Para instalar a solu��o da Biblioteca Digital, baixe o instalador do
reposit�rio da RENAPI atrav�s do comando abaixo:

::

    servidor:~# svn co https://svn.renapi.org/bd/utils/buildout/branches/nsi.deploy/

Com o nsi.deploy baixado, entre no diret�rio e execute o seguinte comando com o
usu�rio `root`:

::

    servidor:~# make

Toda solu��o ser� instalada dentro da pasta `biblioteca_digital` no nsi.deploy.

O servidor de convers�o de documentos � opcional, caso deseje instal�-lo vide a
se��o CloudOOo.

CloudOOo
========


