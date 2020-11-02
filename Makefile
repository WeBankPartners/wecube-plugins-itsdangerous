current_dir=$(shell pwd)
project_name=$(shell basename "${current_dir}")
version=${PLUGIN_VERSION}

clean:
	rm -rf $(current_dir)/dist/

build: clean
	pip3 install wheel
	python3 setup.py bdist_wheel

image: build
	docker build -t $(project_name):$(version) .

package: image
	sed 's/{{PLUGIN_VERSION}}/$(version)/' ./build/register.xml.tpl > ./register.xml
	sed -i 's/{{IMAGENAME}}/$(project_name):$(version)/g' ./register.xml
	sed -i 's/{{CONTAINERNAME}}/$(project_name)-$(version)/g' ./register.xml 
	docker save -o image.tar $(project_name):$(version)
	zip $(project_name)-$(version).zip image.tar register.xml init.sql
	rm -f image.tar
	rm -f register.xml

upload: package
	$(eval container_id:=$(shell docker run -v $(current_dir):/package -itd --entrypoint=/bin/sh minio/mc))
	docker exec $(container_id) mc config host add wecubeS3 $(s3_server_url) $(s3_access_key) $(s3_secret_key) wecubeS3
	docker exec $(container_id) mc cp /package/$(project_name)-$(version).zip wecubeS3/wecube-plugin-package-bucket
	docker stop $(container_id)
	docker rm -f $(container_id)
	rm -rf $(project_name)-$(version).zip
