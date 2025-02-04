VERSION := $(shell \
	curl 'https://api.github.com/repos/efck-chat-keyboard/efck/releases/latest' | \
	grep -oP '(?<=tag_name": "v)[^"]+' )
.PHONY: prepare srpm rpm


prepare:
	dnf -y install rpmdevtools rpm-build
	spectool -g -R $(spec)

srpm: prepare
	rpmbuild -bs --define "app_version $(VERSION)" --define "_srcrpmdir $(outdir)" $(spec)

rpm: prepare
	rpmbuild -bb --define "app_version $(VERSION)" --define "_rpmdir $(outdir)" $(spec)
