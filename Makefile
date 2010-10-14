all: apt gstreamer biblioteca_digital_

apt:
	./helper_scripts/install_apt_packs.sh

gstreamer:
	./helper_scripts/install_gst_packs.sh

cloudooo:
	./helper_scripts/install_cloudooo.sh

biblioteca_digital_:
	./helper_scripts/install_digital_library.sh
