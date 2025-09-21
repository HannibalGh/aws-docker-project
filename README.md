# Docker + AWS Lambda: Dual Runtime (CI-first)

This project extends my earlier **Flask + Docker** API by reusing the same core logic and exposing it in two runtimes:

- **Flask in Docker** – local development/testing with a containerised web app  
- **AWS Lambda** – serverless handler returning the exact same JSON

The goal is to show how the **same Python logic** can run in both containerised and serverless environments, with shared tests and CI.

---

## Project structure
``` bash
aws-docker-project/
├── src/
│ ├── init.py
│ ├── core.py # shared logic: generate numbers, sort, dedupe, timestamp (UTC)
│ ├── web_app.py # Flask adapter (Docker runtime) - preserves JSON key order
│ └── lambda_handler.py # AWS Lambda adapter (serverless runtime)
├── tests/
│ ├── conftest.py # adds project root to sys.path for tests
│ └── test_core.py # validates shape + invariants
├── Dockerfile # multi-stage; env-driven host/port; lean healthcheck
├── requirements.txt # flask + pytest
├── .github/workflows/ci.yml # CI: tests + docker build
├── .gitignore
└── function.zip # (ignored) built only when deploying Lambda
```

## What’s new (vs. previous project)
- Added `src/core.py` that centralises logic shared by Flask and Lambda.
- Added `src/web_app.py` (Flask wrapper) for container runtime.  
- Added `src/lambda_handler.py` (Lambda adapter) for AWS runtime.  
- Test suite (`tests/`) with pytest for core logic.  
- CI (GitHub Actions) runs tests and builds the Docker image on every push/PR

## Prerequisites

- Docker Desktop
- (Optional for local tests) Python 3.12 + pip

## Run locally 
**Docker / Flask**
```bash
docker build -t demo-flask .
docker run --rm -p 7774:7774 demo-flask
```
Open: http://localhost:7774/data

**Tests**
```bash
python -m pip install -r requirements.txt
python -m pytest -q
```
## Deploy the Lambda (manual)
**1. Zip code (must contain only src/ at the root)**
```bash
ni src/__init__.py -ItemType File -Force | Out-Null
Remove-Item function.zip -ErrorAction SilentlyContinue
Compress-Archive -Path src -DestinationPath function.zip -Force
```
**2. Create function (via AWS Console)**

- Lambda → Create function → Author from scratch

- Name: lambda-data-api

- Runtime: Python 3.12 → Create

**3. Upload & set handler**

- Code → Upload `function.zip` → Deploy

- Runtime settings → Edit → Handler: src.lambda_handler.handler → Save

**4. Function URL**

- Configurations → Function URL → Create → Auth type `NONE` → Save

- Copy the URL (located at the top in `Function Overview`)

**5. Test**
- Via browser: Paste Function URL directly into browser

- Via Git Bash terminal:
```bash
curl.exe "<YOUR_FUNCTION_URL>"
```
**Example response**
```json
{
  "data": {
    "unsorted": [11, 3, 24, 3, 25, 1, 26, 12, 18, 27, 16, 10, 24, 14, 29],
    "sorted": {
      "raw": [1, 3, 3, 10, 11, 12, 14, 16, 18, 24, 24, 25, 26, 27, 29],
      "unique": [1, 3, 10, 11, 12, 14, 16, 18, 24, 25, 26, 27, 29]
    }
  },
  "timestamp": "2025-09-19 03:17:14 UTC"
}
```
## Cleanup

**Docker**
```bash
# stop/remove any running containers
docker ps
docker rm -f <container_id>

# remove local lambda test image if you built one
docker rmi aws-lambda-local

# optional tidy
docker system prune -f
```
 
**AWS (if deployed)**
- Remove Function URL (preserves the Lambda), or delete the Lambda entirely
- Optionally delete CloudWatch log group: `/aws/lambda/lambda-data-api`


## Continuous Integration (CI)
Included to ensure tests pass and the Docker image still builds reproducibly; it runs only on GitHub activity (pushes and pull requests), not on local runs or manual AWS uploads.

- Workflow: .github/workflows/ci.yml

- On push/PR:
    - Setup Python 3.12
    - Install deps
    - Run pytest
    - docker build sanity-checks the Dockerfile

No CD yet (deliberate) — see “Future Work”.

## Cost
Stays within the AWS Free Tier (Lambda invocations & logs). Function URL has no extra cost. Docker Desktop is free for personal use.

## Future Work
- Add CD to deploy `src.lambda_handler.handler` automatically to AWS Lambda.  
- Extend test coverage (e.g., Lambda adapter).  
- Explore different integration options, such as API Gateway, for more advanced routing and authentication.  
- Use Terraform or AWS SAM for infrastructure as code.  
