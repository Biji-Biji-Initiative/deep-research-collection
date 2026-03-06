# Executive Summary
Our platform uses **Infisical (secrets.mereka.io)** as the single source of truth for all secret values【10†L6-L13】. Secrets are organized hierarchically by usage context. In practice we have three top‐level folders: `/shared` (global secrets), `/k8s/<service>` (Kubernetes workloads), and `/vps/<service>` (VPS-hosted apps)【9†L47-L52】【43†L77-L85】. Within `/shared` there are subfolders like `ai`, `oauth`, `infra`, `integrations`, `cloudflare`, and `backup` containing cross-cutting keys【43†L13-L22】【43†L63-L71】. Under `/k8s` and `/vps` each application (e.g. `mereka-lms`, `authentik`, `nfc-cards`, `legal-agent`, etc.) has its own folder【43†L117-L127】【49†L1-L4】.

**Strengths:** We have eliminated local `.env` files and now inject all secrets via Infisical. The folder taxonomy is largely implemented as intended (hierarchical by runtime)【52†L63-L68】. A canonical "Infisical context" (a single `.infisical.json` in the infra repo) and wrapper script (`scripts/infisical`) enforce consistent access【9†L43-L51】【21†L35-L43】. A comprehensive secrets contract and path registry exist (in the control-plane repo) that map every secret to its Infisical path and downstream targets【53†L9-L13】【52†L63-L68】. We have also automated drift checks and guardrails (e.g. no repo-local Infisical context, no stray `.env` files)【22†L29-L37】【37†L26-L34】.

**Weaknesses:** Gaps remain between design and practice. The *documented* taxonomy (SPEC-GITOPS-012) only lists some shared folders (cloudflare, infra)【9†L47-L55】, but the *implemented* structure includes additional ones (`/shared/ai`, `/shared/oauth`, `/shared/integrations`, `/shared/backup`)【43†L13-L22】【43†L63-L71】. Some older guides (e.g. the Slackbot docs) still reference paths like `/reka-slackbot/admin-dashboard` without the `/vps` prefix【10†L53-L61】【36†L33-L42】, which conflicts with the new standard. The environment model is partly implicit (using Infisical "environment slug" vs distinct folders) and not always consistent across docs and code. In short, the foundation is solid (centralized, hierarchical, no duplicates)【52†L63-L68】【53†L9-L13】, but the taxonomy and governance details need tightening.

**Recommendations (high-level):** Adopt the SPEC's taxonomy fully by codifying all shared subfolders (AI, OAuth, backup, etc.), and updating any legacy path references (e.g. Slackbot). Continue enforcing the canonical CLI wrapper and path-registry checks. Treat Infisical environments (`prod`/`dev`) through slug and avoid encoding env names in paths. Formalize ownership/rotation in policy and CI. More structure (e.g. service subfolders) may improve clarity as we scale.

# 1. Current State of Infisical Secret Management

- **Source of Truth:** Infisical is _the_ canonical secret store for the organization【10†L6-L14】【53†L3-L11】. No secret values reside elsewhere in version control. All applications expect to fetch secrets from Infisical at runtime.
- **Consumers & Delivery:** Secrets flow downstream in two main ways:
  - **Kubernetes (GKE):** We sync secrets into GCP Secret Manager and pull them into clusters using the External Secrets Operator (ESO)【10†L13-L18】【53†L3-L11】. ESO's `ClusterSecretStore` is configured with Universal Auth credentials to read from Infisical's API (using the shared project slug and environment slug)【36†L91-L100】. Once in K8s, apps get them via `envFrom` on Secrets.
  - **VPS/Standalone Services:** We run `infisical run` at startup (e.g. via PM2) to inject secrets into process environments【10†L15-L18】【21†L55-L63】. A canonical wrapper (`scripts/infisical`) in the infra repo sets the context and provides flags like `--path` and `--recursive`. For example:
    ```
    /home/gurpreet/projects/vps/infrastructure/scripts/infisical \
      run --env=prod --path=/k8s/reka-slackbot \
      --recursive -- pnpm start
    ```
- **Authentication:** Machine identities via Universal Auth are used (service tokens are deprecated)【10†L24-L32】【36†L17-L25】. We mint short-lived Infisical access tokens stored in `~/.config/reka/infisical.env`. CI pipelines and the ESO use the Universal Auth credentials (client ID/secret) stored in K8s Secrets【36†L95-L104】【36†L51-L59】. Scripts warn loudly if no valid token/context is found【21†L43-L52】.
- **Contracts & Documentation:** The `secrets-contract.yaml` (in platform-control-plane) is the authoritative inventory of every secret, including its Infisical path, GCP ID, owners, and rotation policy【53†L3-L11】【52†L63-L68】. It explicitly states Infisical as the single SoT【53†L3-L11】, naming rules (SCREAMING_SNAKE_CASE)【53†L9-L13】, and notes that the current folder structure is "hierarchical (implemented)"【52†L63-L68】. Several runbooks and specs (in vps-infrastructure) detail how to use `infisical run` and structure folders【36†L29-L38】【37†L34-L43】.

# 2. Current Folder / Path Structure

We classify secrets by where they're used: **global/shared**, **K8s workloads**, and **VPS apps**. The implemented Infisical tree (as of Feb 2026) is:

```
/                             (root – now empty)
├── shared/                  # Global/shared secrets
│   ├── ai/                 # AI/LLM keys (OPENAI_*, LANGSMITH, etc)【43†L13-L22】
│   ├── oauth/              # OAuth client creds (GOOGLE_CLIENT_ID/SECRET, etc)【43†L26-L30】
│   ├── infra/              # Infrastructure/admin creds (CONTABO_*, SENTRY_DSN, AWS keys, NGROK_, ADMIN_EMAILS, etc)【43†L31-L39】
│   ├── integrations/       # External service tokens (RUBE_TOKEN, CELERY_URLs, AIRTABLE, CLICKUP_*, WEAVIATE_*, etc)【43†L46-L55】
│   ├── cloudflare/         # DNS/API tokens (CLOUDFLARE_TOKEN_*)【43†L63-L68】
│   └── backup/             # Backup credentials (B2_*, RESTIC_*)【43†L69-L75】
│
├── k8s/                     # Kubernetes service secrets (ESO-managed)
│   ├── authentik/           # SSO service (e.g. JWT, DB creds)
│   ├── listmonk/            # Email marketing
│   ├── n8n/                 # Workflow automation
│   ├── reka-slackbot/       # Slackbot (all subfolders under `reka-slackbot/`)
│   ├── temporal/            # Workflow engine
│   ├── twentycrm/           # CRM
│   ├── mereka-backend/      # (dev cluster, JWT and Stripe secrets)
│   └── mereka-lms/          # Open edX platform (many subfolders)
│
└── vps/                     # VPS-hosted application secrets (injected at runtime)
    ├── g-finances/         # (empty folder; uses imports only)
    ├── legal-agent/        # 3 keys (DATABASE_URL, POSTGRES_PASSWORD, NEXT_PUBLIC_API_BASE_URL)【43†L81-L84】
    ├── nfc-cards/          # App-specific keys (AUTH_SECRET, GOOGLE_CLIENT_SECRET, STRIPE_*, RESEND_*, encryption keys, PocketBase creds, etc)【43†L86-L95】
    ├── reka-admin/         # Admin dashboard (REKA_ADMIN_NEXTAUTH_SECRET only)【50†L1-L4】
    └── spoken/            # (empty folder; uses imports only)
```

- **Normative vs Implemented:** The **SPEC-GITOPS-012** normatively requires `/shared/*`, `/k8s/<service>`, and `/vps/<service>` prefixes【9†L47-L52】, with specific children (`/shared/cloudflare`, `/shared/infra`)【9†L53-L60】. In practice, we have indeed a `/shared` top-level, plus `/k8s` and `/vps`, as shown above【43†L13-L22】【43†L81-L90】. However, the norm does *not* list `/shared/ai`, `/shared/oauth`, `/shared/integrations`, or `/shared/backup`, even though we've created them【43†L13-L22】【43†L69-L75】. Similarly, the old Slackbot docs referred to `/reka-slackbot/admin-dashboard/*` under VPS【10†L9-L18】, but our current *vps-* apps actually use `/vps/reka-admin/` (for the admin dashboard)【50†L1-L4】. We note these gaps in the next section.

- **Folder Tree (Current State):** We reconstruct the live structure from documentation and contract data. In particular, the Infisical-run **VPS hardening** guide lists the initial folder creation plan【37†L36-L44】, and the **folder-structure doc** gives a detailed tree【43†L13-L22】【43†L77-L85】. Key examples:
  - All Slackbot secrets (API keys, tokens) live under `/k8s/reka-slackbot/<component>` for Kubernetes and under `/vps/reka-admin/*` for the VPS admin UI【10†L9-L18】【43†L117-L127】.
  - Shared Dev keys (e.g. OPENAI_API_KEY, WHISPER_*) are in `/shared/ai`【43†L13-L22】.
  - Shared credentials like OAuth clients are in `/shared/oauth`【43†L26-L30】.
  - Infrastructure-level secrets (e.g. Contabo, AWS, ngrok) are in `/shared/infra`【43†L31-L39】.
  - CSI/backup keys are in `/shared/backup`【43†L69-L75】.
  - VPS apps import shared folders as needed (see current imports in [49†L13-L22]).

# 3. Documented vs Implemented Gap Analysis

- **Taxonomy Gaps:** The **official spec** (SPEC-GITOPS-012) mandates `/shared`, `/k8s`, and `/vps` prefixes【9†L47-L52】 and explicitly mentions `/shared/cloudflare` and `/shared/infra` for specific tokens【9†L53-L59】. In reality, our structure includes additional *shared* categories (e.g. `/shared/ai`, `/shared/oauth`, `/shared/integrations`, `/shared/backup`) that are *not listed in the spec*【43†L13-L22】【43†L69-L75】. These were created during the initial rollout【37†L36-L44】, but the spec hasn't been updated.
- **Path Prefix Consistency:** Older docs (and even some CI scripts) sometimes reference paths like `/reka-slackbot/admin-dashboard`【10†L9-L18】【36†L33-L42】. SPEC and current practice use `/vps/<service>`. For example, the admin dashboard's Infisical path is now `/vps/reka-admin`, not `/reka-slackbot/admin-dashboard`. We observed this mismatch: SPEC forbids CLI context in app repos【9†L43-L46】, and the check script prevents any non-`/vps` or `/k8s` context references【22†L69-L78】, but some legacy examples linger.
- **Environment Handling:** Infisical uses a combination of *environment slugs* (e.g. `prod`, `dev`) and *folder paths*. In practice, we keep the same folder paths for dev and prod (no `_dev` suffixes), leveraging Infisical's `--env` flag to pull from the correct workspace. This is implied in usage guides【10†L13-L18】【36†L29-L38】. There is no separate folder tree per environment, but some docs do not clearly explain this model. (The SECRETS-MANAGEMENT guide for Slackbot shows separate K8s vs VPS paths but uses the same folder base for both dev and prod, relying on `--env`.)
- **Registry / Inventory:** SPEC requires a path registry in the control-plane repo【9†L59-L62】. In practice, the `secrets-contract.yaml` serves as that registry. It lists every secret with its Infisical path, and notes the current vs target path【53†L69-L77】【53†L152-L160】. Thus the control-plane is the source-of-truth for "what secrets exist and where" rather than per-app configs.
- **Naming Conventions:** Both the contract and the spec enforce SCREAMING_SNAKE_CASE for secret keys【53†L9-L13】. Implementation-wide, keys follow this (e.g. `OPENAI_API_KEY`, `DATABASE_URL`【10†L49-L57】【43†L86-L95】). The exception is GCP Secret IDs (external sync) which are kebab-case【53†L9-L13】, but that's outside Infisical itself.

# 4. Current Management Practices

- **Access Patterns:** Developers and CI use the central `scripts/infisical` wrapper in the vps-infrastructure repo【9†L43-L46】【21†L13-L21】. This wrapper enforces using the canonical context (`$INFISICAL_CONTEXT_DIR` or the infra repo's `.infisical.json`) and injecting `INFISICAL_TOKEN` if needed【21†L35-L43】【21†L45-L52】. Engineers set `INFISICAL_PATH` and `--env` on the command line; the wrapper then runs `infisical run --path=...` or `infisical secrets get ...`. CI workflows similarly call this script (or the plain CLI with env vars set). There is no direct `infisical login` per-repo in day-to-day use; all context comes from the infra repo or machine identity.
- **Authorization:** We avoid putting any secret token or project ID in code. Machine identity credentials live in a user's `~/.config/reka/infisical.env` or in secured CI variables【36†L59-L67】【36†L49-L56】. K8s ESO uses a Kubernetes secret with Universal Auth creds (created via Infisical) in the `external-secrets` namespace【36†L95-L104】. The above checks ensure no repository has its own `.infisical.json` or hardcoded context paths【22†L55-L64】【22†L69-L78】.
- **Injection Methods:**
  - **K8s:** ESO retrieves secrets from Infisical (via the Infisical ESO provider) and creates native Kubernetes Secrets. Deployments use `envFrom` or templates to consume them. No app reads Infisical directly in K8s; it just sees regular K8s Secret keys (which are named per chart conventions). The secrets-contract YAML even generates ExternalSecret manifests【53†L15-L23】. (Under review is whether we can remove the GCP hop and have ESO fetch directly from Infisical【31†L133-L142】【52†L63-L68】.)
  - **VPS/PM2:** The `infisical run` command (usually as part of the PM2 ecosystem config) starts each app process with secrets injected. For example, the PM2 config for `legal-agent` calls `infisical run` with `--path=/vps/legal-agent` and imports `/shared/ai`, `/shared/oauth`, etc【49†L19-L27】. There are no leftover `.env` files for these apps; the **VPS hardening** initiative migrated all env vars into Infisical folders【37†L48-L56】【37†L109-L117】.
- **Naming, Ownership, Rotation:** Secret keys are SCREAMING_SNAKE_CASE【53†L9-L13】. Every secret has an owner and a rotation policy tracked in the secrets contract【53†L9-L13】. In practice, rotation procedures (e.g. periodic pwd changes) are documented in rotation runbooks. The tagging standard (env tag, owner tag, etc.) is described in `docs/INFISICAL-SECRET-TAGGING.md` (referenced in [10]). Ownership is thus managed via the contract spreadsheet, not via Infisical UI.
- **Governance/Docs:** Engineers consult runbooks (e.g. VPS-HARDENING, K8s deployment guide) for instructions. CI includes checks like `check-canonical-infisical-context.sh`【22†L50-L59】【22†L69-L78】 and `.env` drift scans【37†L104-L113】. New secret folders should be recorded by updating the contracts repo and possibly the read-only docs view under `vps-infrastructure/docs/gitops/INFISICAL-PATHS.md`【9†L59-L62】. In reality, not every path is fully documented in user-facing guides, so some knowledge is tribal (hence this review).

# 5. What Is Working Well

- **Centralization & Single Source:** All secrets reside in one system (Infisical) and are mapped in one contract【53†L3-L11】【52†L63-L68】. No known secret is unmanaged or missing from this inventory.
- **Hierarchical Taxonomy:** The folder hierarchy by runtime/domain is fully implemented【52†L63-L68】. This makes it easy to locate keys by service. E.g. looking under `/vps/legal-agent` or `/k8s/authentik`. Shared folder prefixes (`/shared`) cleanly separate cross-cutting config【9†L47-L52】【43†L13-L22】.
- **Enforced Context & Access:** The canonical context model works. The `scripts/infisical` wrapper (and a GitHub Action) ensure people always run from the infra repo context【22†L15-L23】【21†L35-L43】. The CI guard scripts have caught every instance of a stray `.infisical.json` or path violation【22†L63-L72】.
- **.env Removal:** We successfully removed all local `.env` files from production apps【37†L26-L34】. The evidence shows applications (g-finances, legal-agent, spoken, etc.) now fetch secrets only via Infisical【37†L109-L117】. This greatly reduces risk of checked-in secrets or config drift.
- **Consistency with Standards:** Secret keys are consistently named uppercase with underscores【53†L9-L13】, matching the convention. Paths closely match service names. The secrets contract drives automated EOS deployments and K8s configs, which ensures alignment across repos.

# 6. What Needs Improvement

- **Folder Taxonomy Gaps & Inconsistencies:** The current structure (seen in [43]) includes `/shared/oauth`, `/shared/integrations`, `/shared/ai`, and `/shared/backup`, but these were not part of the original spec【9†L53-L59】. The spec should be updated to reflect these categories. Likewise, `/vps/reka-admin` (for the admin dashboard) is not mentioned in SPEC-012, yet it exists in practice【50†L1-L4】. There is a risk of confusion: e.g. Slack's legacy doc shows `/reka-slackbot/admin-dashboard`【10†L9-L18】, whereas our live path is `/vps/reka-admin`. We need a cleanup to make docs and spec agree with actual folders.
- **Environment Model Clarity:** We mix using Infisical's **environment slug** vs using separate paths for dev/prod. Currently, a single folder (e.g. `/vps/g-finances`) is shared by dev and prod, and we distinguish environments via `--env dev|prod`【37†L52-L60】. This works, but some legacy patterns implied separate branches or folders. We should explicitly document that folder paths are environment-agnostic and that one should always pass `--env`. Mismatches between docs (which often omit `--env` detail) and practice could confuse newcomers.
- **Path Registry Currency:** The spec mandates a maintained path registry (INF-PATH-020)【9†L59-L62】. The `secrets-contract.yaml` is effectively that registry, but it is large and somewhat static. It may not always be fully up-to-date with ephemeral secrets (especially local dev vs prod differences). We should automate validation that every secret fetched by ESO or runtime is covered by the contract.
- **Overlapping Paths / Duplicates:** The contract rules forbid duplicate secret values in more than one path【9†L39-L46】. Currently we have adhered to that, but some Slackbot tokens are split between `/k8s/reka-slackbot` and `/vps/reka-admin` (same key names in both)【10†L53-L61】. This was done for "parity" but can confuse which value is canonical. We should enforce that each key's primary path is single-sourced, and possibly drop redundant copies if unnecessary.
- **Scalability and Depth:** Some folders are very large and could be subdivided. For example, `/vps/nfc-cards` contains dozens of keys and a noted "(optional)" list of many more【43†L86-L95】. It might make sense to break that into subfolders (e.g. `/vps/nfc-cards/payment`, `/vps/nfc-cards/wallet`, etc.) to avoid human error. Similarly, `/shared/integrations` could grow and maybe deserves subfolders per integration team.
- **Governance & Hygiene:** Not all paths have explicit CI enforcement. For example, aside from the context check, we lack an automated check that new folders conform to the spec's prefixes. Some pre-commit hooks are mentioned (e.g. blocking `.env` commits【37†L84-L92】), but nothing prevents an engineer from using a non-canonical path unless an infisical-run fails. We should add policy or automated reviews to catch any new pattern deviations immediately.

# 7. Recommended Future-State Model

- **Finalize Taxonomy:** Update SPEC-GITOPS-012 to list all approved shared subfolders: at least `/shared/ai`, `/shared/oauth`, `/shared/infra`, `/shared/integrations`, `/shared/cloudflare`, `/shared/backup`. Require any new category to follow `/shared/*`. For **VPS apps**, use `/vps/<app>/...` exclusively; include `reka-admin` or rename it `/vps/reka-slackbot-admin/` if consistency is needed. For **K8s apps**, keep `/k8s/<service>/...`.
- **Explicit Imports vs Separation:** For services that run in both contexts (like Slackbot admin dashboard), keep secret names identical but rely on **`--path`** disambiguation. For example, continue using `/vps/reka-admin` for the VPS instance and `/k8s/reka-slackbot` for K8s, but require a policy (and doc) that "Shared secrets (identical names) can live in both paths only if needed; otherwise use a single canonical location."
- **Environment Handling:** Standardize on *one path per value*, with environment coming from the `--env` flag. Deprecate any environment-specific path suffixes. Ensure every doc and script uses `--env`. Possibly include environment tag in contract for clarity, but do not bake it into the folder path.
- **Folder Depth and Naming:** Consider deeper subfolders for complex apps: e.g. `/vps/nfc-cards/payment/SECRET`, `/vps/nfc-cards/wallet/SECRET`. Or namespace by component if the app has clear modules. This could improve manageability. Also audit use of `reka-` vs service names (we have `/reka-admin` vs `/reka-slackbot`), standardize on one approach.
- **Governance Enhancements:** Maintain the secrets contract (or an equivalent manifest) as the live path registry【53†L3-L11】. Generate a human-friendly summary of all Infisical folders for reference (as was done in the legacy README【31†L30-L38】). Implement CI checks that new `infisical run` or ESO configs only reference folders in the registry. Enforce the "no repo-local context" rule by hooking `check-canonical-infisical-context.sh` into CI on all repos.
- **Operational Guardrails:** Update pre-commit and CI to flag:
  - Any secret key not uppercase snake_case (contract rule【53†L9-L13】).
  - Any `.env` additions (as already done【37†L84-L92】).
  - Any new path not under `/shared`, `/k8s/`, or `/vps/`.
  - Possibly use `infisical folders get` in CI to verify expected folder exists before pipelines use it (to catch typos).
- **Rotation & Tagging:** Tighten documentation of rotation. The contract lists rotation policy per secret【53†L9-L13】, but we should ensure the relevant owners know their cadence. Possibly add automated reminders for "manual-yearly" secrets. Tagging (environment, owner, classification) in Infisical should be enforced via templates or sync scripts if not already.

# 8. Migration / Improvement Plan

- **Immediate:**
  - **Documentation Update:** Revise the Infisical path spec (SPEC-GITOPS-012 and internal docs) to include the existing shared subfolders (ai, oauth, integrations, backup)【43†L13-L22】. Update any repo README/runbook to use correct paths (change `/reka-slackbot/admin-dashboard`→`/vps/reka-admin`)【10†L9-L18】【36†L33-L42】. Ensure all references to Infisical usage mention `--env`.
  - **CI Enforcement:** Deploy CI hooks (as per SPEC) to catch any new `.infisical.json` or incorrect context references【22†L69-L78】. Integrate secret-path validation into pipeline (e.g. a list of approved paths).
  - **Folder Creation:** For any shared folder used in practice but missing, create it in Infisical with a placeholder secret (or document it) and add it to the registry. For example, if `/shared/oauth` was added manually, ensure it's recorded. Verify the `/shared` and `/vps` trees match [43].
- **Short-Term:**
  - **Migration of Secrets:** If any secrets are still lingering outside the correct paths (e.g. if dev vs prod diverged), run `infisical-sync-envs.sh` (as in [10†L61-L64]) to align them. Remove any root-level secrets as per the cleanup note【43†L133-L140】.
  - **Refactor Large Folders:** Evaluate splitting overly large folders (like `/vps/nfc-cards`) into logical subfolders. Plan this with the respective app team.
  - **Wrap and Review:** Have each service update its PM2/K8s configs to use the approved paths and `scripts/infisical`. (The rollout steps in SPEC-GITOPS-012【9†L74-L83】 already outline wrapper integration.) Confirm no service still uses local `.env` or hardcoded secrets.
- **Medium-Term:**
  - **CI/CD Integration:** Use the Infisical CLI in CI (or GCP secrets) to supply secrets for builds/tests, replacing any plain-value environment variables. Automate token refresh (e.g. cron `infisical-mint-token.sh` run).
  - **Review and Audit:** Periodically audit the path registry vs actual Infisical content. Use scripts (like drift check) to detect any mismatches【22†L69-L78】. Ensure the contract YAML and Infisical state stay in sync.
  - **Governance:** Finalize rotation policies and tagging standards. Consider additional training or an internal "CLI cheat sheet" for engineers to avoid misuse.

# 9. Final Verdict

Overall, our Infisical setup is **fundamentally sound and maturing**. We have achieved a single secrets store, removed all ad-hoc secrets files, and structured secrets by logical boundaries【53†L3-L11】【52†L63-L68】. The hierarchical model is already implemented and mostly followed. The key remaining issues are administrative (gap-filling, docs alignment, and policy enforcement), not technical failures. In other words, the approach is **good but still evolving**. With the refinements above, we can lock down the process: the core design need not be overhauled, only iteratively improved to reduce remaining inconsistencies.

**Sources:** Internal Infisical specs, runbooks, and code (notably: SPEC-GITOPS-012【9†L47-L52】, the secrets contract【53†L3-L13】【52†L63-L68】, runbook docs【37†L36-L44】【43†L13-L22】, and wrapper/check scripts【21†L35-L43】【22†L69-L78】). These authoritative sources are cited to distinguish policy vs implementation.
