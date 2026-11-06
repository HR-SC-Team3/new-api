<!-- @format -->

# Run the development services with Docker

This guide is for people who have never used Docker. It shows how to start PostgreSQL and
Redis on your computer. The file `docker-compose.yml` is for **development only**.

## What is Docker?

Docker runs programs in small, closed boxes called **containers**. You do not install
PostgreSQL or Redis on your computer. Docker downloads them and runs them in containers.

**Docker Compose** starts several containers with one command. The file
`docker-compose.yml` tells Compose which containers to start.

| Container           | What it does                               | Address on your computer |
| ------------------- | ------------------------------------------ | ------------------------ |
| `cargohub-postgres` | The database (the single source of truth)  | `localhost:5433`         |
| `cargohub-redis`    | The cache (it never replaces the database) | `localhost:6379`         |

Only your own computer can reach these addresses.

## Step 1: Install Docker

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Start Docker Desktop. Wait until it says that Docker is running.
3. Open a terminal and check the install:

    ```bash
    docker --version
    docker compose version
    ```

    Both commands must print a version number.

## Step 2: Create your `.env` file

The containers need passwords. We do not store passwords in git. Each person makes a private
`.env` file.

1. Copy the example file:

    ```bash
    cp .env.example .env
    ```

    On Windows PowerShell, use `Copy-Item .env.example .env`.

2. Open `.env` and replace each `change-me` with your own password.
3. Use the **same** passwords in `DATABASE_URL` and `REDIS_URL`.

Never commit `.env`. Git already ignores it.

## Step 3: Start the services

Open a terminal in the project folder. Run:

```bash
docker compose up -d
```

- The first start downloads the images. This can take a few minutes.
- `-d` means "detached". The containers run in the background.

## Step 4: Check that it works

```bash
docker compose ps
```

Wait until the **STATUS** column shows `healthy` for both containers. This takes about
30 seconds.

## Daily commands

| Task                              | Command                        |
| --------------------------------- | ------------------------------ |
| Start the services                | `docker compose up -d`         |
| Stop the services (keep the data) | `docker compose stop`          |
| Show the status                   | `docker compose ps`            |
| Show the logs                     | `docker compose logs -f`       |
| Show the logs of one service      | `docker compose logs -f redis` |
| Stop and remove the containers    | `docker compose down`          |

`docker compose down` keeps your data. The data lives in **volumes** (`postgres_data` and
`redis_data`).

## Start again from zero

> **Warning:** This command deletes all data in your local database and cache.

```bash
docker compose down -v
docker compose up -d
```

Do this if you change `POSTGRES_PASSWORD` after the first start. PostgreSQL stores the
password in its volume when it first starts. A new value in `.env` has no effect until you
delete the volume.

## Troubleshooting

| Problem                                               | Cause and fix                                                                                         |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `Set POSTGRES_PASSWORD in .env` (or `REDIS_PASSWORD`) | Your `.env` file is missing or has no value for that name. Do Step 2 again.                           |
| `Cannot connect to the Docker daemon`                 | Docker Desktop is not running. Start it and wait.                                                     |
| `port is already allocated`                           | Another program uses port 5433 or 6379 (maybe a PostgreSQL or Redis you installed). Stop it.          |
| Login to the database fails                           | The password in `.env` does not match the old volume. Run `docker compose down -v`, then start again. |
| A container shows `unhealthy`                         | Run `docker compose logs <service>` and read the last lines.                                          |

## Rules for this file

- `docker-compose.yml` is for development. Do not use it in production.
- Do not write passwords in `docker-compose.yml`. Put them in `.env`.
- Do not commit `.env`. Only commit `.env.example`, with fake values.
