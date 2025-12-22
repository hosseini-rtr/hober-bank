build:
	docker compose -f local.yml up --build -d --remove-orphans
up:
	docker compose -f local.yml up -d --remove-orphans
down:
	docker compose -f local.yml down

down-v:
	docker compose -f local.yml down -v

banker-config:
	docker compose -f local.yml config

makemigerations:
	docker compose -f local.yml run --rm api python manage.py makemigrations

migrate:
	docker compose -f local.yml run --rm api python manage.py migrate

collecstatic:
	docker compose -f local.yml run --rm api python manage.py collecstatic --no-input --clear

createsuperuser:
	docker compose -f local.yml run --rm api python manage.py createsuperuser

flush:
	docker compose -f local.yml run --rm api python manage.py flush

network-inspect:
	docker network inspect banker_local_nw

banker-db:
	docker compose -f local.yml exec postgres psql --username=ur_hober_bank --dbname=db_hober_bank

create-test-superuser:
	docker compose -f local.yml run --rm api \
	python manage.py create_test_superuser

portainer:
	docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-v portainer_data:/data portainer/portainer-ce:lts