all: gstreamer

gstreamer:
	./helper_scripts/install_apt_packs.sh
	./helper_scripts/install_gst_packs.sh
