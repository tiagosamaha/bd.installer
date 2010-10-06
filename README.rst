Instalação
==========

Para instalar a Biblioteca Digital no Debian você deve habilitar o repositório "unstable". Para habilitar este repositório, adicione no arquivo `/etc/apt/source.list` as seguintes linhas:
    
    deb http://ftp.br.debian.org/debian/ sid main contrib non-free
    deb-src http://ftp.br.debian.org/debian/ sid main contrib non-free
    
    deb ftp://ftp.debian-multimedia.org sid main non-free
    deb-src ftp://ftp.debian-multimedia.org sid main non-free

Agora atualize o apt com esse comando:
    apt-get update

e instale o pacote "debian-multimedia-keyring" com esse comando:
    apt-get install debian-multimedia-keyring

e atualize o apt novamente.

Atualize o debian com os pacotes instaveis:
    apt-get -y --force-yes dist-upgrade

Verifique se todos os pacotes foram instalados corretamente.
