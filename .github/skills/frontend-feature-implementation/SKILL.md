```skill
---
name: frontend-feature-implementation
description: End-to-end workflow for implementing frontend features in this React + Vite monorepo. Use when turning openapi.json endpoints into TypeScript types, API client functions, MSW mock handlers, React Query hooks, Zustand stores, and page components. Covers the full cycle from type generation to MSW/real-backend toggle verification.
---

# Frontend Feature Implementation

## Overview

Translate backend API endpoints (defined in docs/openapi.json) into fully working frontend features with MSW mock support, following the conventions established in the user management and auth flows.

## Stack

- React 19 + Vite 7 + TypeScript (strict)
- TanStack Router (file-based) + TanStack Query + TanStack Table
- Zustand for auth state, React Query for server state
- axios with shared client (`src/api/client.ts`)
- shadcn/ui (Radix UI) + Tailwind CSS 4
- MSW 2 (browser service worker) for mock mode
- openapi-typescript for type generation

## Workflow

### Step 0: Generate TypeScript types from openapi.json

Run from `frontend/`:

```bash
npx openapi-typescript ../docs/openapi.json -o src/api/generated/schema.d.ts
```

This produces `components['schemas']` types that all endpoint files import from. Regenerate whenever openapi.json changes.

### Step 1: Define API endpoint functions

Create or update files in `src/api/endpoints/`. Each file groups related endpoints.

Pattern:

```typescript
import { apiClient } from '../client'
import { type components } from '../generated/schema'

// ---- Types derived from openapi schema ----
export type MyRequest = components['schemas']['MyRequest']
export type MyResponse = components['schemas']['MyResponse']

// ---- API functions ----
export async function myEndpoint(data: MyRequest): Promise<MyResponse> {
  const res = await apiClient.post<MyResponse>('/api/v1/...', data)
  return res.data
}
```

Conventions:
- Export type aliases from `components['schemas']` at file top.
- Return `res.data` (unwrap axios response).
- Use `void` return for 204 No Content endpoints.
- Keep `apiClient` (from `src/api/client.ts`) as the sole HTTP layer; never import axios directly.

Reference files: `src/api/endpoints/account.ts`, `src/api/endpoints/users.ts`.

### Step 2: Write MSW mock handlers

Create handler files in `src/mocks/handlers/`. Each mirrors an endpoint file.

Pattern:

```typescript
import { http, HttpResponse } from 'msw'
import { BASE_URL } from '../config'
import { db } from '../data/db'

export const myHandlers = [
  http.get(`${BASE_URL}/api/v1/...`, ({ cookies }) => {
    if (!cookies.access_token) {
      return HttpResponse.json({ error: 'Not authenticated.' }, { status: 401 })
    }
    // ... business logic against in-memory db
    return HttpResponse.json(responseData, { status: 200 })
  }),
]
```

Conventions:
- Always prefix paths with `${BASE_URL}` (from `src/mocks/config.ts`). MSW matches absolute URLs from axios, not relative paths.
- MSW service worker responses cannot set `document.cookie` via `Set-Cookie` header. For auth flows, the frontend hook must manually call `setCookie()` when `VITE_ENABLE_MSW === 'true'`.
- Register new handler arrays in `src/mocks/handlers/index.ts`.
- Seed data in `src/mocks/data/db.ts` should match feature file Given conditions.
- Auth guard pattern: check both `cookies.access_token && db.getCurrentUser()` to handle stale cookies after frontend restart (in-memory db resets but browser cookies persist).

Reference files: `src/mocks/handlers/account.ts`, `src/mocks/handlers/users.ts`, `src/mocks/data/db.ts`.

### Step 3: Create React Query hooks

Place hooks in `src/features/<domain>/api/`.

Query hook:

```typescript
import { useQuery } from '@tanstack/react-query'
import { myEndpoint, type MyParams } from '@/api/endpoints/my'

export const MY_QUERY_KEY = 'my-resource'

export function useMyResource(params?: MyParams) {
  return useQuery({
    queryKey: [MY_QUERY_KEY, params],
    queryFn: () => myEndpoint(params),
  })
}
```

Mutation hook:

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { createResource, type CreateRequest } from '@/api/endpoints/my'
import { MY_QUERY_KEY } from './use-my-resource'

export function useCreateResource() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateRequest) => createResource(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MY_QUERY_KEY] })
      toast.success('Resource created.')
    },
  })
}
```

Conventions:
- Export query key constants for cache invalidation.
- Mutations invalidate related query keys in `onSuccess`.
- Use `toast` from `sonner` for success/error feedback.

### Step 4: Update Zustand store (if needed)

Auth state lives in `src/stores/auth-store.ts`. Only modify for auth-related features.

For server state (lists, CRUD), use React Query exclusively — do not duplicate into Zustand.

### Step 5: Build page and feature components

- Routes live in `src/routes/` (TanStack Router file-based routing).
- Feature components live in `src/features/<domain>/components/`.
- Data schemas for table columns in `src/features/<domain>/data/`.

Authenticated routes are nested under `src/routes/_authenticated/`. The route guard in `_authenticated/route.tsx` checks the `access_token` cookie and hydrates the auth store by calling `getMe()`.

Conventions:
- Use shadcn/ui components from `src/components/ui/`.
- Use `useListX` hooks for data fetching with loading/error states.
- Use `useMutationX` hooks for form submissions.
- Follow existing dialog patterns: provider context + dialog components.

### Step 6: Verify

1. TypeScript check: `npx tsc --noEmit`
2. Production build: `npx vite build`
3. Mock mode: `pnpm dev:mock` — verify full flow with MSW
4. API mode: `pnpm dev:api` — verify with real backend

## MSW / Real Backend Toggle

| Mode | Command | Env file | `VITE_ENABLE_MSW` |
|------|---------|----------|-------------------|
| Mock | `pnpm dev:mock` | `.env.mock` | `true` |
| Real API | `pnpm dev:api` | `.env.api` | `false` |
| Default dev | `pnpm dev` | `.env.development` | `true` |

MSW is conditionally started in `src/main.tsx` via `enableMocking()`.

## Key Gotchas

- **MSW URL matching**: axios sends absolute URLs (`http://localhost:8000/api/v1/...`). Handlers MUST use `${BASE_URL}/api/v1/...`, not relative `/api/v1/...`.
- **MSW cannot set cookies**: Service Worker intercepted responses do not write to `document.cookie`. Manually call `setCookie()`/`removeCookie()` in hooks when `import.meta.env.VITE_ENABLE_MSW === 'true'`.
- **Stale cookies across restarts**: Browser cookies persist but MSW in-memory db resets. Auth guards must check both cookie AND db state.
- **204 vs 200 in mocks**: If the real backend returns 204 (no body), the mock should also return 204. If the frontend needs data from the response, add a separate query endpoint (e.g., `GET /me`) rather than changing the mock to return body data.
- **Type generation**: Always regenerate `schema.d.ts` after openapi.json changes. Never hand-edit generated types.

## Directory Structure Reference

```
src/
├── api/
│   ├── client.ts                     # Shared axios instance
│   ├── generated/schema.d.ts         # Auto-generated from openapi.json
│   └── endpoints/                    # API function files
│       ├── account.ts
│       └── users.ts
├── mocks/
│   ├── browser.ts                    # setupWorker
│   ├── config.ts                     # BASE_URL for handler paths
│   ├── data/db.ts                    # In-memory mock DB + seed data
│   └── handlers/                     # MSW handler files
│       ├── index.ts                  # Handler registry
│       ├── account.ts
│       └── users.ts
├── features/<domain>/
│   ├── api/                          # React Query hooks
│   │   ├── use-list-*.ts
│   │   └── use-create-*.ts
│   ├── components/                   # UI components
│   └── data/                         # Table schemas, constants
├── stores/
│   └── auth-store.ts                 # Zustand auth state
└── routes/
    ├── _authenticated/               # Protected routes
    │   └── route.tsx                 # Auth guard + getMe() hydration
    └── (auth)/                       # Public auth pages
        ├── sign-in.tsx
        └── sign-up.tsx
```

## Output Checklist

- [ ] `schema.d.ts` regenerated from latest openapi.json
- [ ] Endpoint functions in `src/api/endpoints/` with proper types
- [ ] MSW handlers in `src/mocks/handlers/` with `BASE_URL` prefix
- [ ] Seed data in `src/mocks/data/db.ts` matching feature file conditions
- [ ] Handler registry updated in `src/mocks/handlers/index.ts`
- [ ] React Query hooks in `src/features/<domain>/api/`
- [ ] Page components using hooks with loading/error states
- [ ] `tsc --noEmit` passes
- [ ] `vite build` passes
- [ ] `pnpm dev:mock` flow works end-to-end
```
