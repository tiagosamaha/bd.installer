FOLDER=$(cd $(dirname $0); pwd)
echo -n "Deseja instalar o CloudOOo [s/n]? "
read opcao
case $opcao in
    s)
        wget -O /tmp/ez_setup.py http://peak.telecommunity.com/dist/ez_setup.py
        python2.6 /tmp/ez_setup.py
        mkdir -p /etc/cloud3o/run
        svn co https://svn.erp5.org/repos/public/erp5/trunk/utils/cloudooo /etc/cloud3o/cloudooo
        cat /etc/cloud3o/cloudooo/cloudooo/samples/sample.conf | sed "/working_path/s/\/hd\/cloudooo/\/etc\/cloud3o/g" > /etc/cloud3o/cloudooo.conf
        python2.6 /etc/cloud3o/cloudooo/setup.py install;
        wget -O /tmp/openoffice.tar.gz http://download.services.openoffice.org/files/stable/3.2.1/OOo_3.2.1_Linux_x86_install-deb_en-US.tar.gz
        tar xvvf /tmp/openoffice.tar.gz -C /tmp
        cd /tmp/OOO*/DEBS
        dpkg -i *.deb
        cd $FOLDER
        echo ""
        echo "Execute: paster server /etc/cloud3o/cloudooo.conf";;
    n)
        echo "Instalação concluída!"
        exit;;
    *)
        echo "Opção inválida."
        sleep 1
        instalar_cloudooo;;
esac

