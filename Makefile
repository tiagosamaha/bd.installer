all:
	./helper_scripts/install_apt_packs.sh
	gstreamer
	biblioteca_digital

gstreamer:
	./helper_scripts/install_gst_packs.sh

biblioteca_digital:
	./helper_scripts/install_digital_library.sh
