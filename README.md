# README.md

## dev

### Build

```bash
docker build -t xiserver .
```

### Run

```bash
docker run -d -p 8081:8000 xiserver
```

or

```bash
uvicorn main:app --reload
```

## prod

If you pudate dependencies, update requirements.txt in dev container.

```bash
uv pip freeze > requirements.txt
```

```bash
git pull origin main
```

```bash
docker build -t xiserver .
```

```bash
sudo systemctl stop xiserver.service
```

```bash
docker remove xiserver-container
```

```bash
docker create --name xiserver-container -p 8081:8000 xiserver
```

```bash
sudo systemctl start xiserver.service
```

see : https://www.notion.so/VPS-fbe6d657375f46c49d6d9e6bb4cc8cd7?pvs=4#124c18040bfe808095edd50e84c24962
