sudo docker create -v ${1}:/employees-build-scripts -v ${2}:/var/lib/postgresql/data --name ${3} -p 5432:5432 $(sudo docker build -q .)
