# Custom Exception Handling in FastAPI

A concise reference summarizing scalable patterns, trade‑offs, and recommended best practices for defining and routing custom exceptions in FastAPI applications.

---

## 1. Overview

Clear, maintainable error handling is critical as APIs grow. Custom exceptions allow you to:

* Encapsulate domain errors (e.g., `CartEmpty`, `InvalidToken`).
* Provide self‑documenting defaults for HTTP status and messages.
* Expose structured data (IDs, retry hints) to clients and logs.
* Separate **domain logic** (`raise`) from **transport logic** (HTTP response). 

We reviewed multiple approaches and settled on a hybrid that balances defaults, flexibility, and per‑error control.

---

## 2. Approaches Reviewed

| Approach                               | How It Works                                                                                                        | Pros                                                                         | Cons                                                                                                      |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **1. Fully Generic Handler**           | One `@app.exception_handler(Exception)` uses `exc.status_code` and `vars(exc)` to build JSON.                       | • Minimal setup<br>• Automatic for all domain errors                         | • Central handler grows complex<br>• Hard to add headers or special logic                                 |
| **2. Static Style**             | Empty exception classes; each registered with a handler closed over a static `initial_detail`.                      | • Domain code decoupled from messages<br>• Handlers know full static payload | • Cannot include per‑instance data<br>• Message tweaks require handler edit                               |
| **3. Factory + Per‑Type Registration** | Each exception class has its own lightweight handler via a factory (`create_exception_handler(status, detail_fn)`). | • No giant `if` chains<br>• Flexible per‑error JSON/body/logging/headers     | • Requires one registration per exception type                                                            |
| **4. Single Base‑Class Handler**       | All domain exceptions inherit from `AppException`; one handler for that base class loops over `vars(exc)`.          | • One handler covers all AppExceptions<br>• Auto‑picks extra attrs           | • Mixing different payloads may need branching<br>• Per‑error headers or metrics need `isinstance` checks |

---

## 3. Selected Hybrid Best Practice

We combine the clarity of **class‑level defaults** with **raise‑time overrides**, and use **per‑type handler registration** that simply reads the exception instance. 

### 3.1. Exception Class Definition

```python
# exceptions.py
from typing import Any

class AppException(Exception):
    """Base for all domain errors: default status, detail, plus arbitrary attrs."""
    status_code: int = 400
    detail: str = "An error occurred."

    def __init__(
        self,
        *,
        detail: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        for key, value in kwargs.items():
            setattr(self, key, value)

# Example subclass with required field and default override
class CartEmpty(AppException):
    status_code = 404
    detail = "Your cart is empty."

    def __init__(self, *, cart_id: str, detail: str | None = None):
        super().__init__(detail=detail, status_code=self.status_code, cart_id=cart_id)
```

* **Class‑level defaults** (`status_code`, `detail`) are immediately visible.
* **Raise‑time overrides** let you customize `detail=` (or even `status_code=`) without subclassing further.
* **Extra kwargs** become instance attributes (`cart_id`, `user_id`, etc.).

### 3.2. Handler Factory

```python
# handlers.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Callable, Any

DetailFn = Callable[[Exception], Any]

def create_exception_handler(
    status_code: int,
    detail_fn: DetailFn,
) -> Callable:
    async def handler(request: Request, exc: Exception):
        try:
            # Build body from exception instance
            body = detail_fn(exc)
            code = status_code
        except Exception:
            # Handler bug or missing attr → Internal Server Error
            body = {"message": str(exc)}
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=code, content=body)
    return handler
```

* **Reads** `exc.status_code`, `exc.detail`, and any extra attributes via `detail_fn`.
* **Defensive fallback** escalates handler errors to 500, preserving JSON shape.

### 3.3. Registration

```python
# main.py
from fastapi import FastAPI
from exceptions import CartEmpty, AppException
from handlers import create_exception_handler

app = FastAPI()

# Per‑type handlers
app.add_exception_handler(
    CartEmpty,
    create_exception_handler(
        status_code=CartEmpty.status_code,
        detail_fn=lambda exc: {
            "message": exc.detail,
            "cart_id": exc.cart_id,
        },
    ),
)
# …register other exceptions similarly…

# Fallback for any unhandled AppException subclass
app.add_exception_handler(
    AppException,
    create_exception_handler(
        status_code=AppException.status_code,
        detail_fn=lambda exc: {"message": exc.detail},
    ),
)

# Global fallback for truly unexpected errors
app.add_exception_handler(
    Exception,
    create_exception_handler(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail_fn=lambda exc: {"message": "Internal server error."},
    ),
)
```

* **Per‑error routing** via exception class.
* **Co‑located registration** with domain exception definitions.
* **Global fallback** ensures no error ever leaks without a JSON response.

---

## 4. Trade‑Offs & Rationale

1. **Class‑Level Defaults vs Raise‑Time Only**

   * Defaults on the class make HTTP mapping discoverable; overrides at raise time add flexibility without new subclasses.
   * Pure raise‑time parameters scatter defaults across code, hindering discoverability.

2. **Per‑Type Handlers vs One Generic Handler**

   * Per‑type avoids a giant `if isinstance` and enables custom headers/metrics.
   * One generic handler simplifies registration but may bloat with special cases.

3. **Factory vs Bespoke Functions**

   * Factory reduces boilerplate while keeping each handler isolated.
   * Hand‑written handlers offer full control but repeat boilerplate.

4. **Static Payloads vs Dynamic**

   * Static (Bookly) is simplest when no instance data is needed.
   * Dynamic (reading `exc` in handler) is essential for per‑instance details like IDs or retry hints.

This hybrid pattern evolved by asking:

* **Where do I want to see default codes & messages?** (class)
* **Where do I need custom context?** (raise site overrides)
* **How do I ensure predictable JSON for every error?** (defensive factory)
* **How do I keep domain and transport logic separate?** (per‑type registration)

By combining these, you get a scalable, self‑documenting, and robust exception‑handling architecture.

---

