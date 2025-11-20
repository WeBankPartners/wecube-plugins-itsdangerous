current_dir=$(shell pwd)
project_name ?= $(shell basename "${current_dir}")
version=${PLUGIN_VERSION}
arch ?= amd64          # 默认amd64，可选 ARCH=amd64/arm64

clean:
	rm -rf package
	rm -rf $(current_dir)/dist/
	rm -rf $(current_dir)/ui/dist/

build: clean
	pip3 install wheel
	python3 setup.py bdist_wheel
	docker run --rm  -v $(current_dir):/home/node/app -w /home/node/app node:16.20.2 sh -c "npm set registry https://mirrors.cloud.tencent.com/npm/ && cd /home/node/app/ui && npm install --force && npm run plugin"

image: build
ifeq ($(arch),arm64)
	docker buildx build --platform linux/arm64 -t $(project_name):$(version) . --load
else
	docker build -t $(project_name):$(version) .
endif

package: image
	rm -rf package
	mkdir -p package
	echo "$(version)" > VERSION
	cd package && sed 's/{{PLUGIN_VERSION}}/$(version)/' ../build/register.xml.tpl > ./register.xml
	cd package && sed -i 's/{{IMAGENAME}}/$(project_name):$(version)/g' ./register.xml
	cd package && sed -i 's/{{CONTAINERNAME}}/$(project_name)-$(version)/g' ./register.xml 
	cd package && docker save -o image.tar $(project_name):$(version)
	cd ui/dist && zip -9 -r ui.zip .
	cd package && mv ../ui/dist/ui.zip .
	cd package && cp ../init.sql ./init.sql
	cd package && zip -9 $(project_name)-$(version)-$(arch).zip image.tar register.xml ui.zip init.sql
	cd package && rm -f image.tar
	cd package && rm -f register.xml
	cd package && rm -f ui.zip
	cd package && rm -f init.sql
	docker rmi $(project_name):$(version)

upload: package
	$(eval container_id:=$(shell docker run -v $(current_dir)/package:/package -itd --entrypoint=/bin/sh minio/mc))
	docker exec $(container_id) mc config host add wecubeS3 $(s3_server_url) $(s3_access_key) $(s3_secret_key) wecubeS3
	docker exec $(container_id) mc cp /package/$(project_name)-$(version)-$(arch).zip wecubeS3/wecube-plugin-package-bucket
	docker stop $(container_id)
	docker rm -f $(container_id)
	rm -rf $(project_name)-$(version)-$(arch).zip
