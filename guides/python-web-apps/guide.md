# Modern Python Web Applications for ASP.NET Core Developers

A practical guide to building APIs and server-rendered web applications in Python, organized in the same conceptual order as an ASP.NET Core learning path. The goal is not to translate C# to Python line by line. The goal is to understand the ASP.NET Core concepts you already know, then learn the modern Python patterns, libraries, tradeoffs, and production habits that solve the same problems.

## Who This Is For

You know .NET and ASP.NET Core. You know the Python language well enough to read and write Python, but you want a guided path through the web ecosystem: project layout, routing, dependency injection, validation, persistence, authentication, authorization, security, deployment, background work, HTTP clients, and testing.

## Framework Choice

This guide uses **FastAPI** as the main framework because it maps naturally to ASP.NET Core APIs:

- Route functions feel close to minimal API endpoint handlers.
- Type hints and Pydantic models give request binding, validation, response shaping, and OpenAPI output.
- Dependencies provide a practical request-scoped composition model.
- Starlette underneath supplies middleware, routing, responses, sessions, templates, static files, and ASGI integration.
- The testing story is direct, using HTTPX-style clients and dependency overrides.

The guide also introduces **Jinja2 templates with FastAPI/Starlette** for server-rendered pages. When a concept is better served by Django's integrated ecosystem, the chapter calls that out. Django is Python's closest analogue to a large batteries-included framework with built-in admin, forms, ORM, authentication, sessions, CSRF protection, and security defaults. Flask appears only as context because it is useful historically and for small apps, but it is not the recommended default for this learning path.

## Core Stack

Use this stack for the capstone unless a chapter explicitly explores an alternative:

| Concern | Python choice | ASP.NET Core mental model |
| --- | --- | --- |
| Web framework | FastAPI | Minimal APIs plus MVC/Web API concepts |
| ASGI server | Uvicorn or Granian | Kestrel hosting process |
| Validation and DTOs | Pydantic v2 | Model binding, validation attributes, API contracts |
| Database ORM | SQLAlchemy 2.x | EF Core, but more explicit |
| Migrations | Alembic | EF Core migrations |
| Templates | Jinja2 via Starlette | Razor views/pages conceptually, not syntactically |
| Password hashing | pwdlib or passlib with Argon2/bcrypt | ASP.NET Identity password hashing |
| JWT | PyJWT or python-jose | Bearer token authentication |
| Settings | pydantic-settings | `IConfiguration` plus options binding |
| Tests | pytest, HTTPX, pytest-asyncio | xUnit plus WebApplicationFactory |
| HTTP client | HTTPX | IHttpClientFactory plus HttpClient |
| Background jobs | ARQ, Celery, Dramatiq, or APScheduler | hosted services, queues, workers |
| Observability | structlog/logging, OpenTelemetry, Sentry | logging providers, tracing, health checks |

## Capstone: RecipeVault

The running project is RecipeVault, a recipe management app that grows from a tiny JSON API into a secure, database-backed, tested, deployable web application.

By the end, RecipeVault has:

- Public recipe browsing.
- Authenticated recipe creation and editing.
- User accounts with password hashing.
- Role-based admin features.
- A relational database and migrations.
- API endpoints with OpenAPI documentation.
- Server-rendered HTML pages.
- Form validation, CSRF protection for browser workflows, and secure cookies.
- JWT bearer authentication for API clients.
- Structured logging, health checks, and deployment settings.
- Background jobs for import/export or image processing.
- Unit, integration, and end-to-end style tests.

## Table of Contents

1. Getting Started with Modern Python Web Apps
2. Understanding the Python Web Stack
3. Your First Application
4. Middleware and the ASGI Pipeline
5. JSON APIs with FastAPI
6. Routing
7. Request Binding and Validation
8. Dependency Injection and Dependencies
9. Registering Services and Application Composition
10. Configuration and Settings
11. Documenting APIs with OpenAPI
12. Saving Data with SQLAlchemy and Alembic
13. Creating a Website with Templates
14. Mapping URLs to Pages
15. Generating Responses with Handlers
16. Binding and Validating Forms
17. Rendering HTML with Jinja2
18. Building Forms and Reusable UI Helpers
19. Creating a Website with Controller-Style Routers
20. Creating HTTP APIs with Router Modules
21. Filters, Dependencies, and Cross-Cutting Concerns
22. Creating Custom Request Components
23. Authentication
24. Authorization
25. API Authentication and Bearer Tokens
26. Logging and Troubleshooting
27. Publishing and Deployment
28. HTTPS, TLS, and Proxy-Aware Apps
29. Security Best Practices
30. Application Startup, Lifespan, and Hosting
31. Advanced Configuration
32. Custom Web Components and Framework Extensions
33. Calling Remote APIs
34. Background Tasks and Services
35. Unit Testing
36. Testing Web Applications
37. Capstone Build Plan

## 1. Getting Started with Modern Python Web Apps

ASP.NET Core gives you a project template, `Program.cs`, a dependency injection container, configuration providers, middleware, and Kestrel. In Python, you assemble those pieces more explicitly. That is empowering, but it can feel underspecified at first.

The Python version of "create a new web project" is usually:

1. Create a virtual environment.
2. Add dependencies to `pyproject.toml`.
3. Create an ASGI app object.
4. Run the app with a server such as Uvicorn.
5. Add tests from the beginning.

Recommended starting layout:

```text
recipevault/
  pyproject.toml
  src/
    recipevault/
      __init__.py
      main.py
      settings.py
      api/
      web/
      domain/
      data/
      services/
  tests/
```

`src/` layout avoids accidental imports from the working directory and makes packaging behavior more honest. This is more ceremony than a small script needs, but it pays off for real applications.

Minimal app:

```python
# src/recipevault/main.py
from fastapi import FastAPI

app = FastAPI(title="RecipeVault")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Run it:

```bash
uvicorn recipevault.main:app --reload
```

Modern Python web development rewards explicitness. You choose the application structure, dependency boundaries, test style, and persistence approach. The job of this guide is to give you a default path so every choice is not a research project.

## 2. Understanding the Python Web Stack

ASP.NET Core applications run through Kestrel and an HTTP middleware pipeline. Python has two major web server interfaces:

- **WSGI**: older synchronous interface used by Flask and classic Django deployments.
- **ASGI**: modern async-capable interface used by FastAPI, Starlette, Django async features, and websockets.

FastAPI is an ASGI app. Uvicorn receives HTTP traffic, converts it into ASGI events, and passes those events to FastAPI. FastAPI delegates much of the low-level web behavior to Starlette.

Mental model:

| ASP.NET Core | Python/FastAPI |
| --- | --- |
| Kestrel | Uvicorn, Granian, Hypercorn |
| `WebApplication` | FastAPI app object |
| Middleware pipeline | ASGI middleware stack |
| Minimal API endpoint | path operation function |
| Controllers | APIRouter modules |
| Model binding | type hints plus Pydantic |
| `IConfiguration` | settings class and environment variables |
| DI container | FastAPI dependencies plus manual composition |

Python's ecosystem is less centralized than .NET. That means fewer official one-size-fits-all answers, but also less framework gravity. Your production skill is knowing which choices to standardize inside your own project.

## 3. Your First Application

Start with a vertical slice: route, model, service, test. Do not start with a grand architecture.

```python
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field

app = FastAPI(title="RecipeVault")


class RecipeSummary(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=120)
    servings: int = Field(ge=1, le=50)


RECIPES = {
    1: RecipeSummary(id=1, title="Sourdough Pancakes", servings=4),
}


@app.get("/api/recipes/{recipe_id}", response_model=RecipeSummary)
def get_recipe(
    recipe_id: Annotated[int, Path(ge=1)],
) -> RecipeSummary:
    recipe = RECIPES.get(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
```

Key ideas:

- Type hints are runtime inputs for FastAPI.
- Pydantic models describe validated data contracts.
- `HTTPException` is the normal way to stop request handling with a specific HTTP result.
- `response_model` shapes output and OpenAPI metadata.

In .NET, you might separate DTOs, entities, services, and endpoints immediately. In Python, begin simple, then extract when there is real pressure. Python projects become hard to maintain when they are either too clever or too flat for too long.

## 4. Middleware and the ASGI Pipeline

ASP.NET Core middleware wraps the request delegate. ASGI middleware does the same conceptual job: inspect or modify requests and responses around downstream handling.

Common Python middleware:

- CORS middleware.
- Trusted host middleware.
- HTTPS redirect middleware, depending on deployment.
- Session middleware for cookie-backed browser sessions.
- Custom correlation ID or request logging middleware.

Example:

```python
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://recipes.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", "generated-later")
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response
```

Best practice:

- Keep middleware small.
- Use dependencies for endpoint-specific behavior.
- Use middleware for truly cross-cutting behavior.
- Be careful with request body reads inside middleware; body streams can be consumed.
- Put proxy, HTTPS, host, and CORS decisions in deployment-aware configuration.

## 5. JSON APIs with FastAPI

FastAPI's core strength is JSON APIs with typed contracts. This is the closest match to ASP.NET Core minimal APIs and Web API controllers.

```python
from fastapi import status
from pydantic import BaseModel, Field


class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    instructions: str = Field(min_length=1)
    servings: int = Field(ge=1, le=50)


class RecipeRead(RecipeCreate):
    id: int


@app.post(
    "/api/recipes",
    response_model=RecipeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_recipe(command: RecipeCreate) -> RecipeRead:
    recipe_id = max(RECIPES) + 1
    recipe = RecipeRead(id=recipe_id, **command.model_dump())
    RECIPES[recipe_id] = recipe
    return recipe
```

Use separate models for:

- Create input.
- Update input.
- Public read output.
- Internal persistence entities.

Do not return ORM models directly from every endpoint just because it works. Shape your API contract deliberately. This is the same discipline as keeping EF Core entities from leaking into every public API response.

## 6. Routing

ASP.NET Core endpoint routing maps URLs and HTTP verbs to handlers. FastAPI routes are path operation decorators.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("")
def list_recipes():
    ...


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int):
    ...


@router.put("/{recipe_id}")
def replace_recipe(recipe_id: int):
    ...
```

Register routers in the app:

```python
from recipevault.api import recipes

app.include_router(recipes.router)
```

Routing best practices:

- Use plural resource names for REST-style resources.
- Keep route modules cohesive by feature, not by HTTP verb.
- Use `APIRouter` for modularity.
- Put shared dependencies on routers when every endpoint in that router needs them.
- Avoid ambiguous routes such as `/{id}` and `/search` in surprising order. Prefer explicit prefixes.

## 7. Request Binding and Validation

ASP.NET Core binds route values, query strings, headers, forms, and bodies. FastAPI does the same using function parameters, `Annotated`, and Pydantic models.

```python
from typing import Annotated

from fastapi import Header, Query
from pydantic import BaseModel, Field


class RecipeSearch(BaseModel):
    q: str | None = Field(default=None, max_length=100)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


@router.get("")
def search_recipes(
    filters: Annotated[RecipeSearch, Query()],
    accept_language: Annotated[str | None, Header()] = None,
):
    ...
```

Python validation practices:

- Prefer Pydantic constraints over manual `if` checks for shape validation.
- Keep business rules in services or domain functions.
- Use `field_validator` and `model_validator` for validation that belongs to the data contract.
- Return consistent error shapes. FastAPI gives a default `422` validation response; decide whether to keep it or wrap it.

ASP.NET Core developers often ask where validation attributes went. In Python, validation usually lives in Pydantic model fields and validators.

## 8. Dependency Injection and Dependencies

ASP.NET Core has a full DI container with singleton, scoped, and transient lifetimes. FastAPI has dependency functions. They are less formal, but request-scoped composition is excellent.

```python
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


DbSession = Annotated[Session, Depends(get_db)]


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int, db: DbSession):
    return recipes_service.get_recipe(db, recipe_id)
```

Dependency functions can depend on other dependencies. This gives a graph similar to DI, but it is resolved by FastAPI for each request.

Use dependencies for:

- Database sessions.
- Current user.
- Authorization checks.
- Settings access.
- Parsed request context.
- Feature flags.
- Unit-of-work or service objects.

Do not hide all construction behind dependencies. Plain Python constructors are good. Dependency injection is a tool, not the whole architecture.

## 9. Registering Services and Application Composition

ASP.NET Core centralizes registration in `Program.cs` and extension methods. Python usually uses explicit module-level composition.

Recommended pattern:

```python
# src/recipevault/app_factory.py
from fastapi import FastAPI

from recipevault.api import recipes, users
from recipevault.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.include_router(recipes.router)
    app.include_router(users.router)
    return app
```

Then:

```python
# src/recipevault/main.py
from recipevault.app_factory import create_app

app = create_app()
```

Benefits:

- Tests can create app instances with test settings.
- Startup composition is centralized.
- Routers stay focused.
- Deployment imports a stable `app`.

Python service registration is often "just imports and constructors." Use that until you need something more formal. If you introduce a DI container library, document why.

## 10. Configuration and Settings

ASP.NET Core has layered configuration providers and options binding. Python commonly uses environment variables with a typed settings class.

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RECIPEVAULT_",
        extra="ignore",
    )

    app_name: str = "RecipeVault"
    database_url: str = Field(default="sqlite:///recipevault.db")
    secret_key: str
    debug: bool = False
```

Rules:

- Treat settings as immutable values at app startup.
- Never commit real secrets.
- Use `.env` only for local development.
- In production, use the host's secret manager or environment injection.
- Fail fast when required settings are missing.
- Keep framework settings separate from domain configuration.

Configuration is one area where Python is more fragmented than .NET. Pick one settings approach and use it everywhere.

## 11. Documenting APIs with OpenAPI

FastAPI generates OpenAPI from routes, type hints, Pydantic models, status codes, tags, summaries, descriptions, and security dependencies.

```python
@router.post(
    "",
    response_model=RecipeRead,
    status_code=201,
    summary="Create a recipe",
    responses={
        409: {"description": "A recipe with this title already exists"},
    },
)
def create_recipe(command: RecipeCreate, db: DbSession) -> RecipeRead:
    ...
```

Good API documentation is not accidental:

- Use descriptive route tags.
- Use dedicated response models.
- Document non-2xx responses.
- Keep examples realistic.
- Do not expose internal fields.
- Prefer generated OpenAPI, then customize when needed.

OpenAPI is also a contract. If client teams depend on your schema, test it or snapshot it.

## 12. Saving Data with SQLAlchemy and Alembic

EF Core is integrated into the .NET ecosystem. SQLAlchemy is powerful, mature, and more explicit. Alembic handles migrations.

SQLAlchemy 2.x declarative model:

```python
from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    servings: Mapped[int] = mapped_column(nullable=False)
```

Repository-style function:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_recipe(session: Session, recipe_id: int) -> Recipe | None:
    return session.get(Recipe, recipe_id)


def list_recipes(session: Session) -> list[Recipe]:
    statement = select(Recipe).order_by(Recipe.title)
    return list(session.scalars(statement))
```

Important differences from EF Core:

- SQLAlchemy sessions are units of work and identity maps, but they are not thread-safe.
- You must decide sync vs async database access. Do not mix casually.
- Explicit transactions are your friend.
- Lazy loading under async can surprise you. Prefer eager loading for relationship-heavy queries.
- Migrations are generated by Alembic, reviewed by humans, and applied in deployment.

For a newcomer, start with synchronous SQLAlchemy inside FastAPI unless you have a strong async database requirement. Sync database calls are commonly deployed behind multiple worker processes or threads. Async is powerful, but it adds constraints and does not automatically make database-bound apps faster.

## 13. Creating a Website with Templates

ASP.NET Core offers Razor Pages and MVC views. FastAPI does not include a page framework, but Starlette supports Jinja2 templates.

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/recipes", response_class=HTMLResponse)
def recipes_index(request: Request):
    recipes = recipes_service.list_public_recipes()
    return templates.TemplateResponse(
        "recipes/index.html",
        {"request": request, "recipes": recipes},
    )
```

Python template guidance:

- Keep templates dumb. Business logic belongs in services.
- Use template inheritance for layout.
- Use partial templates for repeated UI.
- Escape by default. Jinja2 escapes HTML in configured environments.
- Add CSRF protection for browser forms.

If you want a deeply integrated server-rendered framework, Django is usually the better Python choice. FastAPI plus Jinja2 is excellent when your app is API-first and needs some server-rendered pages.

## 14. Mapping URLs to Pages

Razor Pages map page files to routes. FastAPI maps functions to URLs. To keep page routes maintainable, group them by feature.

```text
src/recipevault/
  web/
    __init__.py
    recipes.py
    account.py
  templates/
    layout.html
    recipes/
      index.html
      detail.html
      edit.html
```

```python
# web/recipes.py
router = APIRouter(prefix="/recipes", tags=["web-recipes"])


@router.get("")
def index(request: Request):
    ...


@router.get("/{recipe_id}")
def detail(recipe_id: int, request: Request):
    ...
```

The equivalent of Razor Page route conventions is your project convention. Write it down:

- Browser routes live under `web/`.
- JSON routes live under `api/`.
- Shared domain logic lives outside both.
- Templates mirror route modules.

This keeps your web and API surfaces from becoming tangled.

## 15. Generating Responses with Handlers

ASP.NET Core handlers return `IResult`, `IActionResult`, model objects, redirects, files, or pages. FastAPI handlers can return Python data, response objects, redirects, streaming responses, files, or template responses.

```python
from fastapi.responses import FileResponse, RedirectResponse


@router.post("/recipes/{recipe_id}/publish")
def publish_recipe(recipe_id: int):
    recipes_service.publish(recipe_id)
    return RedirectResponse(
        url=f"/recipes/{recipe_id}",
        status_code=303,
    )


@router.get("/exports/{export_id}")
def download_export(export_id: str):
    path = export_service.get_export_path(export_id)
    return FileResponse(path, filename="recipes.csv")
```

Response rules:

- For APIs, return validated models and status codes.
- For browser posts, redirect after successful form submission.
- For downloads, use file responses.
- For long-running exports, start a job and return a status URL.
- For errors, use consistent exception handling.

HTTP semantics matter in Python just as much as in .NET.

## 16. Binding and Validating Forms

HTML forms are not JSON. FastAPI can bind form fields, but it is more manual than Pydantic JSON bodies.

```python
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, Field, ValidationError


class RecipeForm(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    instructions: str = Field(min_length=1)
    servings: int = Field(ge=1, le=50)


@router.post("/recipes/new")
def create_recipe_from_form(
    request: Request,
    title: Annotated[str, Form()],
    instructions: Annotated[str, Form()],
    servings: Annotated[int, Form()],
):
    try:
        form = RecipeForm(
            title=title,
            instructions=instructions,
            servings=servings,
        )
    except ValidationError as error:
        return templates.TemplateResponse(
            "recipes/new.html",
            {"request": request, "errors": error.errors()},
            status_code=400,
        )
    ...
```

For heavy form workflows, Django becomes attractive because forms, model forms, CSRF, sessions, auth, and admin are integrated. In FastAPI, you can still build excellent form flows, but you own more of the conventions.

## 17. Rendering HTML with Jinja2

Razor views and Jinja2 templates solve the same broad problem: mix static markup with server-provided data.

Jinja2 layout:

```html
<!-- templates/layout.html -->
<!doctype html>
<html lang="en">
  <head>
    <title>{% block title %}RecipeVault{% endblock %}</title>
  </head>
  <body>
    <main>{% block content %}{% endblock %}</main>
  </body>
</html>
```

Page:

```html
{% extends "layout.html" %}

{% block title %}Recipes{% endblock %}

{% block content %}
  <h1>Recipes</h1>
  <ul>
    {% for recipe in recipes %}
      <li><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></li>
    {% endfor %}
  </ul>
{% endblock %}
```

Template practices:

- Pass view models, not raw database sessions.
- Use macros or partials for repeated markup.
- Keep filters simple.
- Use explicit URLs instead of stringly route construction when your routing helper supports it.
- Never mark user content as safe unless it is sanitized.

## 18. Building Forms and Reusable UI Helpers

ASP.NET Core Tag Helpers reduce repetitive form markup. In Python/Jinja2, use macros, partial templates, or a form library.

Jinja2 macro:

```html
{% macro field(name, label, value="", errors=[]) %}
  <label for="{{ name }}">{{ label }}</label>
  <input id="{{ name }}" name="{{ name }}" value="{{ value|e }}">
  {% if errors %}
    <p class="error">{{ errors[0] }}</p>
  {% endif %}
{% endmacro %}
```

Use it:

```html
{% from "forms.html" import field %}

{{ field("title", "Title", form.title, errors.title) }}
```

Good helper design:

- Keep helpers visual, not business-aware.
- Let handlers decide data and validation.
- Prefer a small set of project macros over a large custom template framework.
- For complex form-heavy apps, evaluate Django forms before building your own mini-framework.

## 19. Creating a Website with Controller-Style Routers

MVC controllers group related actions. In FastAPI, `APIRouter` modules fill that role.

```python
# web/account.py
router = APIRouter(prefix="/account", tags=["account"])


@router.get("/login")
def login_page(request: Request):
    ...


@router.post("/login")
def login_submit(request: Request):
    ...


@router.post("/logout")
def logout():
    ...
```

Controller-style organization:

- `api/recipes.py` for API recipes.
- `web/recipes.py` for browser recipes.
- `services/recipes.py` for use cases.
- `data/models.py` and `data/repositories.py` for persistence.
- `domain/recipes.py` for domain rules that should not know HTTP exists.

Avoid placing all logic in route functions. Route functions should translate HTTP into application calls and translate results back into HTTP.

## 20. Creating HTTP APIs with Router Modules

ASP.NET Core Web API controllers often use attributes, filters, route prefixes, and action results. FastAPI router modules give the same larger-scale organization.

```python
router = APIRouter(
    prefix="/api/recipes",
    tags=["recipes"],
    responses={404: {"description": "Not found"}},
)


@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(
    recipe_id: int,
    patch: RecipePatch,
    db: DbSession,
    user: CurrentUser,
) -> RecipeRead:
    return recipes_service.update_recipe(db, recipe_id, patch, user)
```

API module practices:

- One router per feature or bounded context.
- Keep request and response models near the API module or in `schemas/`.
- Keep persistence models separate.
- Use dependencies for auth, database, and contextual concerns.
- Use service functions for workflows that combine validation, persistence, and side effects.

FastAPI makes it easy to write route functions that do everything. Resist that ease once the route stops being trivial.

## 21. Filters, Dependencies, and Cross-Cutting Concerns

ASP.NET Core has filters for MVC and Razor Pages. FastAPI does not have the same filter taxonomy. The closest tools are:

- Dependencies for preconditions and request-scoped values.
- Middleware for cross-cutting request/response wrapping.
- Custom `APIRoute` classes for advanced route behavior.
- Exception handlers for consistent error translation.

Authorization dependency:

```python
from fastapi import Depends, HTTPException, status


def require_admin(user: CurrentUser) -> None:
    if "admin" not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
```

Apply to a route:

```python
@router.delete(
    "/{recipe_id}",
    dependencies=[Depends(require_admin)],
    status_code=204,
)
def delete_recipe(recipe_id: int, db: DbSession) -> None:
    recipes_service.delete_recipe(db, recipe_id)
```

Use the smallest mechanism that fits. Do not build a filter framework until your app proves it needs one.

## 22. Creating Custom Request Components

ASP.NET Core lets you build custom middleware, filters, model binders, and result types. FastAPI and Starlette let you build custom dependencies, middleware, routes, exception handlers, and response classes.

Custom exception mapping:

```python
class RecipeNotFound(Exception):
    def __init__(self, recipe_id: int):
        self.recipe_id = recipe_id


@app.exception_handler(RecipeNotFound)
async def recipe_not_found_handler(request: Request, exc: RecipeNotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Recipe {exc.recipe_id} was not found"},
    )
```

Custom route behavior is powerful but should be rare. Prefer plain route functions, dependencies, and exception handlers. Framework extension points are for repeated infrastructure behavior, not for avoiding simple code.

## 23. Authentication

ASP.NET Core Identity is a complete membership system. FastAPI does not ship an equivalent. You choose:

- Use an external identity provider such as Auth0, Entra ID, Cognito, Clerk, or FusionAuth.
- Use a library such as fastapi-users when it fits.
- Build a small local account system when requirements are modest.
- Use Django if you want integrated auth, admin, sessions, permissions, and forms.

For RecipeVault, build a modest local account system so you understand the moving parts.

Password rules:

- Store password hashes, never passwords.
- Use Argon2id or bcrypt through a maintained password hashing library.
- Use secure random reset tokens with expiration.
- Rate-limit login and reset attempts.
- Rotate session identifiers on login.

Session login flow for browser UI:

1. User posts email and password.
2. Handler loads user by normalized email.
3. Password hash is verified.
4. Session cookie stores a server-side or signed session identifier.
5. Current user dependency loads the user for each request.

FastAPI can use Starlette's session middleware, but serious production systems often use server-side session storage or external identity providers.

## 24. Authorization

Authentication answers "who are you?" Authorization answers "what may you do?"

Python patterns:

- Role checks: simple and common.
- Policy functions: close to ASP.NET Core authorization policies.
- Resource-based checks: user may edit this specific recipe if they own it.
- Permission tables: useful for admin-heavy apps.
- External policy engines: useful in larger systems.

Resource authorization:

```python
def ensure_can_edit_recipe(user: User, recipe: Recipe) -> None:
    if recipe.owner_id == user.id:
        return
    if "admin" in user.roles:
        return
    raise Forbidden("You cannot edit this recipe")
```

Keep authorization near the use case. Route-level dependencies are good for broad requirements such as "must be logged in." Resource-specific authorization usually belongs in the service layer after loading the resource.

## 25. API Authentication and Bearer Tokens

ASP.NET Core APIs commonly use JWT bearer authentication. FastAPI supports OAuth2 and bearer token dependencies, but you must decide token issuing, validation, and claims mapping.

JWT guidance:

- Prefer external identity providers for production when possible.
- Validate issuer, audience, expiration, signature, and algorithm.
- Keep access tokens short-lived.
- Use refresh tokens carefully and store them securely.
- Do not put sensitive data in JWT payloads.
- Treat scopes/claims as inputs to authorization, not authorization by themselves.

FastAPI dependency shape:

```python
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


async def get_current_api_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    claims = token_service.validate_access_token(token)
    return users_service.get_user_by_subject(claims.sub)
```

For browser apps, prefer secure cookies plus CSRF protection. For API clients, bearer tokens are normal. Do not use local storage for highly sensitive browser tokens if a cookie-based flow is viable.

## 26. Logging and Troubleshooting

ASP.NET Core has structured logging abstractions. Python has standard `logging`, plus libraries such as structlog and loguru. For production services, prefer standard logging plus structured output.

```python
import logging

logger = logging.getLogger(__name__)


def publish_recipe(recipe_id: int, user_id: int) -> None:
    logger.info(
        "Publishing recipe",
        extra={"recipe_id": recipe_id, "user_id": user_id},
    )
```

Production logging practices:

- Log structured fields, not only prose.
- Include request ID or trace ID.
- Avoid logging secrets, tokens, passwords, and personal data.
- Log at boundaries: request, command, external call, background job, exception.
- Use exception logging with stack traces for unexpected failures.
- Add health endpoints and readiness checks.

Troubleshooting Python apps also means understanding import paths, virtual environments, process managers, worker counts, and environment variables. Many "framework bugs" are actually deployment shape bugs.

## 27. Publishing and Deployment

ASP.NET Core deployments publish build output. Python deployments usually install your package and run an ASGI server.

Common production options:

- Container image running Uvicorn or Granian.
- Platform-as-a-service deployment.
- VM with systemd and reverse proxy.
- Kubernetes with health checks and config injection.

Container outline:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install .

CMD ["uvicorn", "recipevault.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deployment checklist:

- Set `SECRET_KEY`, database URL, allowed hosts, and CORS origins.
- Run migrations before serving new code.
- Serve static files through a CDN or reverse proxy when appropriate.
- Use multiple workers for CPU-bound or blocking sync workloads.
- Add liveness and readiness endpoints.
- Capture logs centrally.
- Monitor errors and latency.

Do not rely on `--reload` outside development.

## 28. HTTPS, TLS, and Proxy-Aware Apps

ASP.NET Core often handles forwarded headers and HTTPS redirection. Python apps are commonly behind a reverse proxy, load balancer, or platform edge.

Key decisions:

- TLS usually terminates at the proxy or platform.
- The app must understand forwarded scheme and host headers.
- Cookies must be `Secure`, `HttpOnly`, and use an appropriate `SameSite` setting.
- HSTS belongs at the edge or app, but configure it deliberately.
- CORS is not a security boundary. It is browser behavior.

Proxy-aware concerns:

- Generate correct absolute URLs.
- Redirect to HTTPS only when the app knows the original scheme.
- Trust forwarded headers only from trusted proxies.
- Set allowed hosts to prevent host header attacks.

In FastAPI/Starlette deployments, read your ASGI server and platform docs carefully. This area is deployment-specific.

## 29. Security Best Practices

Security in Python web apps is a combination of framework features, dependencies, deployment, and habits.

Core checklist:

- Validate all input at boundaries.
- Use parameterized SQL through SQLAlchemy.
- Escape HTML output; do not mark user content safe.
- Add CSRF protection to cookie-authenticated form posts.
- Use secure cookies.
- Hash passwords with modern password hash algorithms.
- Rate-limit login, reset, and expensive endpoints.
- Keep dependencies updated and scan them.
- Do not expose debug tracebacks in production.
- Keep secrets out of Git.
- Use least privilege database credentials.
- Add authorization tests for sensitive workflows.

FastAPI is excellent for APIs, but it does not automatically provide every browser security feature that Django includes. If you build server-rendered forms in FastAPI, explicitly add CSRF protection and secure session handling.

## 30. Application Startup, Lifespan, and Hosting

ASP.NET Core has host startup, dependency registration, and app lifetime events. FastAPI uses lifespan events for startup and shutdown.

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = Settings()
    app.state.http_client = httpx.AsyncClient(timeout=5)
    yield
    await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)
```

Use lifespan for:

- Creating shared clients.
- Verifying critical configuration.
- Connecting to telemetry.
- Warming caches when necessary.
- Closing resources cleanly.

Do not do slow, fragile work in startup unless the app truly cannot serve without it. For migrations, prefer deployment steps over app startup migrations in most production systems.

## 31. Advanced Configuration

Once RecipeVault grows, split configuration by concern.

```python
from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    url: str
    echo_sql: bool = False


class SecuritySettings(BaseSettings):
    secret_key: str
    access_token_minutes: int = 15
    cookie_secure: bool = True


class Settings(BaseSettings):
    database: DatabaseSettings
    security: SecuritySettings
```

Advanced configuration practices:

- Validate settings at startup.
- Use typed URLs and constrained values where useful.
- Avoid global mutable settings.
- Keep test settings explicit.
- Separate public config from secrets.
- Document required environment variables.

In .NET, options validation is a named feature. In Python, your settings model is the validation layer.

## 32. Custom Web Components and Framework Extensions

ASP.NET Core developers often build custom model binders, tag helpers, middleware, and filters. Python gives you several smaller extension points.

Useful extension targets:

- Pydantic custom types for reusable validation.
- FastAPI dependencies for request-specific services.
- Starlette middleware for cross-cutting behavior.
- Jinja2 filters and macros for presentation helpers.
- Exception handlers for domain-to-HTTP mapping.
- Custom response classes for specialized output.

Example custom Pydantic type usage:

```python
from pydantic import BaseModel, Field


class SlugCommand(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
```

Extension rule: start boring. Most teams need fewer framework extensions than they think. Reach for custom components only when repeated code becomes harder to understand than the abstraction.

## 33. Calling Remote APIs

ASP.NET Core uses `HttpClientFactory` to manage clients and avoid socket exhaustion. Python commonly uses HTTPX.

```python
import httpx


class NutritionClient:
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url

    async def estimate_calories(self, ingredients: list[str]) -> int:
        response = await self._client.post(
            f"{self._base_url}/estimate",
            json={"ingredients": ingredients},
        )
        response.raise_for_status()
        data = response.json()
        return int(data["calories"])
```

Practices:

- Reuse clients. Do not create a new client per request.
- Set timeouts.
- Handle retries only for safe operations or explicitly idempotent commands.
- Use circuit breakers or backoff for fragile dependencies.
- Log remote failures with correlation IDs.
- Hide vendor payloads behind your own client interface.

Register shared HTTP clients in lifespan or app state, then inject wrapper clients through dependencies.

## 34. Background Tasks and Services

ASP.NET Core has hosted services and background services. FastAPI has in-process background tasks, but they are only suitable for small, non-critical follow-up work.

Use in-process background tasks for:

- Sending a low-risk notification after a response.
- Writing an audit event when losing it is acceptable.
- Small cleanup work.

Use a real worker queue for:

- Email delivery that must retry.
- Image processing.
- Long imports and exports.
- Scheduled jobs.
- Work that must survive app restarts.

Python worker choices:

- Celery: mature, widely used, heavier.
- Dramatiq: simpler queue workers.
- ARQ: asyncio Redis queue.
- RQ: straightforward Redis jobs.
- APScheduler: scheduling inside a process, not a durable queue by itself.

RecipeVault background work:

- Import recipes from a URL.
- Export a user's recipes to CSV.
- Generate search indexes.
- Send account emails.

Keep background job code in application services so the web request and worker can call the same use case safely.

## 35. Unit Testing

ASP.NET Core developers often use xUnit, Moq, and FluentAssertions. Python's standard path is pytest.

Domain test:

```python
import pytest

from recipevault.domain.recipes import RecipeDraft


def test_recipe_title_is_required():
    with pytest.raises(ValueError):
        RecipeDraft(title="", instructions="Mix.", servings=2)
```

Service test:

```python
def test_owner_can_publish_recipe(fake_repo):
    service = RecipeService(fake_repo)
    recipe = service.publish(recipe_id=1, user_id=42)
    assert recipe.is_published
```

Testing practices:

- Keep domain tests fast and framework-free.
- Use fakes for simple ports.
- Use real database tests for repository behavior.
- Avoid over-mocking SQLAlchemy sessions.
- Name tests as behavior, not implementation.
- Use fixtures for setup, but keep them readable.

Python tests are pleasant when your application logic is not trapped inside route functions.

## 36. Testing Web Applications

FastAPI testing uses a test client for HTTP-level tests and dependency overrides for test seams.

```python
from fastapi.testclient import TestClient

from recipevault.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Dependency override:

```python
def override_current_user():
    return User(id=1, email="admin@example.com", roles=["admin"])


app.dependency_overrides[get_current_user] = override_current_user
```

Integration test levels:

- Route test with fake dependencies.
- Route test with real database transaction.
- Repository test against test database.
- Browser-level test with Playwright if the UI becomes important.
- Contract test for OpenAPI schema.

For database tests, prefer isolated transactions, test containers, or a dedicated test database. SQLite is useful, but it is not a perfect substitute for PostgreSQL behavior.

## 37. Capstone Build Plan

Build RecipeVault in slices. Each slice should have code, tests, and a visible result.

### Slice 1: Project Skeleton

- Create `pyproject.toml`.
- Add FastAPI, Uvicorn, Pydantic, pytest, and HTTPX.
- Add `src/recipevault/main.py`.
- Add `/health`.
- Add the first test.

### Slice 2: Recipe API

- Add create, list, get, update, and delete endpoints.
- Use Pydantic create/read/update models.
- Use in-memory storage only for this slice.
- Add validation tests and OpenAPI inspection.

### Slice 3: Database

- Add SQLAlchemy models.
- Add session dependency.
- Add Alembic migrations.
- Replace in-memory storage with repositories.
- Add repository tests.

### Slice 4: Server-Rendered Pages

- Add Jinja2 templates.
- Add recipe list, detail, create, and edit pages.
- Redirect after successful form posts.
- Render validation errors.

### Slice 5: Authentication

- Add users table.
- Add password hashing.
- Add login/logout pages.
- Add current user dependency.
- Add secure session cookies.

### Slice 6: Authorization

- Add owner checks for editing recipes.
- Add admin role.
- Add route-level and service-level authorization tests.

### Slice 7: API Bearer Tokens

- Add token endpoint.
- Add JWT validation dependency.
- Protect write API endpoints.
- Add token expiration tests.

### Slice 8: Security Hardening

- Add CSRF protection for browser forms.
- Add secure cookie settings.
- Add trusted host and CORS configuration.
- Add rate limiting for login.
- Review error handling.

### Slice 9: Observability

- Add structured logging.
- Add request ID middleware.
- Add health and readiness endpoints.
- Add error tracking integration.

### Slice 10: Background Work

- Add export request endpoint.
- Queue export job.
- Store export status.
- Download completed CSV.

### Slice 11: Deployment

- Add container file.
- Add production settings documentation.
- Add migration command.
- Add smoke test.

### Slice 12: Final Testing Pass

- Unit tests for domain rules.
- Integration tests for API flows.
- Web tests for form workflows.
- Authorization regression tests.
- OpenAPI contract review.

## Python Web Ecosystem Map

| If you need... | Start with... | Notes |
| --- | --- | --- |
| API-first service | FastAPI | Best default for this guide |
| Traditional server-rendered app with admin | Django | Strong integrated defaults |
| Tiny custom app or extension point | Flask | Simple, but you assemble more pieces |
| Typed validation | Pydantic | Used heavily by FastAPI |
| ORM and SQL control | SQLAlchemy | Explicit and powerful |
| Integrated ORM plus admin | Django ORM | Best inside Django projects |
| Durable workers | Celery, Dramatiq, ARQ | Choose based on infrastructure |
| HTTP clients | HTTPX | Sync and async APIs |
| Tests | pytest | Dominant Python testing style |

## Recommended Learning Order

1. Build FastAPI endpoints with Pydantic models.
2. Learn dependencies and request-scoped database sessions.
3. Learn SQLAlchemy 2.x and Alembic.
4. Add Jinja2 templates for server-rendered pages.
5. Add authentication and authorization.
6. Add security hardening for browser workflows.
7. Add tests at domain, service, route, and database levels.
8. Add deployment and observability.
9. Learn Django separately so you can recognize when integrated conventions beat assembling pieces yourself.

## Source Notes

This guide is an original Python learning path organized around ASP.NET Core concepts. The chapter order mirrors an ASP.NET Core study sequence, but the explanations, examples, and recommendations are Python-specific.

Primary references used for ecosystem alignment:

- FastAPI documentation: https://fastapi.tiangolo.com/
- Pydantic documentation: https://docs.pydantic.dev/
- SQLAlchemy documentation: https://docs.sqlalchemy.org/
- Alembic documentation: https://alembic.sqlalchemy.org/
- Django security documentation: https://docs.djangoproject.com/en/5.2/topics/security/
- Python Packaging User Guide: https://packaging.python.org/
