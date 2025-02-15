GIT_ROOT:=$(shell git rev-parse --show-toplevel)

servername=canvascoordinator_prime
ha_hostname=
ha_username=root
build_dir=_tmp_build
data_mount=./tmp/

install_ha_addon:
	test ! -z "${ha_hostname}"
	test ! -z "${ha_username}"
	@# Ensure folders exists
	ssh ${ha_username}@${ha_hostname} 'test -d /addons'
	ssh ${ha_username}@${ha_hostname} 'mkdir -p /addons/${servername}'
	@# Empty source directory?
	@# Make package
	rm -fr ${build_dir}
	mkdir -p ${build_dir}
	git ls-files \
		./canvas_coordinator/ \
		./shared/ \
		| xargs -I {} cp --parents "{}" ${build_dir}
	mkdir ${build_dir}/canvas_coordinator_docker
	cp --parents ./canvas_coordinator_docker/install_fonts.sh ${build_dir}
	cp ./canvas_coordinator_docker/Dockerfile ${build_dir}
	cp ./canvas_coordinator_docker/config.yaml ${build_dir}
	cp ./canvas_coordinator_docker/run.sh ${build_dir}
	scp -r ${build_dir}/* ${ha_username}@${ha_hostname}:/addons/${servername}/

docker-build:
	docker build -t ${servername} -f ./canvas_coordinator_docker/Dockerfile .

docker-run:
	mkdir -p ${data_mount}
	docker run -t -v ${data_mount}:/data/ ${servername}

docker-run-bash:
	docker run -ti --entrypoint sh ${servername}
