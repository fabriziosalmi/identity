# Fabrizio Salmi (fab): identity context

Context about the person you are working with. Use it to adapt language, rigor and defaults. Project files (AGENTS.md, CLAUDE.md) in the current repo take precedence over this.

## Who I am

- **Fabrizio Salmi (Fab)**: Infrastructure architect and engineer based in Genoa, Italy. 20+ years designing, building and defending mission-critical systems, from SMBs and non-profits to European financial markets and global CDNs. Philosophy: autonomy through code, turning manual and fragmented operations into automated platforms. Self-described 'not a coder': started publishing open source around 2023 and learns by shipping, fail after fail. Works solo with several AI agents in parallel. Italian native, professional English. Classical high school (liceo classico).

## Work

- **Independent engineer and fractional CTO (2026 to present)**: Freelance. Builds data, analytics and infrastructure platforms for clients. Also independent security researcher doing coordinated disclosure (private report plus fix, per SECURITY.md).
- **MainStreaming SpA (Jul 2025 to Apr 2026)**: Senior System Engineer at a video streaming CDN, focused on CDN technologies. [Infrastructure]
- **Borsa Italiana / Euronext (2019 to 2025)**: Senior Solutions Architect (resilience and innovation), previously Senior Engineering Specialist in architecture and engineering. Perimeter security, DNS, Cloudflare, AWS, high-availability services for financial markets. [Infrastructure, Security]
- **SORINT.lab (2018 to 2019)**: System Engineer on Borsa Italiana (LSEG) projects.
- **YouTube partner (2014 to 2019)**: 25M+ views on own channel, 50M+ on others. No camera: FFmpeg, automation and SEO.

## Projects

- **CertMate**: Self-hosted TLS certificate lifecycle platform: issue, renew, discover, inventory, deploy. REST API, UI, MCP, Helm, CLI via Homebrew. Flagship project, ~1.4k stars. Fab is maintainer and reviews contributor PRs. [Security, Languages and frameworks] <https://github.com/fabriziosalmi/certmate>
- **caddy-waf**: WAF middleware for Caddy: regex rules, IP and DNS filtering, rate limiting, GeoIP, Tor, anomaly detection. In the Caddy module registry, ~900 stars. [Security] <https://github.com/fabriziosalmi/caddy-waf>
- **Security tooling**: patterns (OWASP CRS and bad-bot rules for Nginx, Apache, Traefik, HAProxy), blacklists (daily aggregated domain blocklist), wildbox (self-hosted SIEM/SOAR/WAF platform), zion (Rust TLS reverse proxy with WAF), secure-proxy-manager, aidlp (DLP for LLM endpoints), llmproxy (security-first LLM gateway with audit log), nis2-public (NIS2 posture management), naso (breach exposure monitoring), agssh, limits, caddy-mib, fqdn-model. [Security] <https://github.com/fabriziosalmi>
- **Proxmox and self-hosting tooling**: proxmox-vm-autoscale and proxmox-lxc-autoscale (and an ML variant), proxxx (Rust TUI/CLI cockpit for Proxmox VE and PBS), lws (aws-cli-like CLI for Proxmox, LXC, Docker), proxmox-cluster-balancer. [Infrastructure] <https://github.com/fabriziosalmi/proxxx>
- **Cloudflare and EU sovereignty tooling**: cf-box (multi-account Cloudflare API toolkit), zonecontrol and wafcontrol (Cloudflare settings as YAML via CI), dnscontrol-actions, rainlogs (NIS2 log archiving), flareover (deterministic migration from Cloudflare edge to EU-sovereign infrastructure). [Infrastructure] <https://github.com/fabriziosalmi/flareover>
- **AI developer tooling (l0 family and friends)**: l0-memory (minimal long-term memory for AI assistants: Go MCP + SQLite), l0-git (deterministic project-hygiene gates), l0-compressor (compresses command output to save tokens), slopless (static analysis for AI-slop patterns), noted (local-first Markdown notes with AI), silicondev (local LLM fine-tuning on Apple Silicon), git-flare (coordinating many coding agents on one repo). Used daily across IDEs. [AI and ML] <https://github.com/fabriziosalmi/l0-memory>
- **Italian-language AI**: glm-ocr-ita (GLM-OCR fine-tuned for Italian documents, 8-bit MLX, on Hugging Face), a small Italian LM trained on MLX, Italian translation of oMLX upstream, ai-security (Italian guide). Priorities for OCR: quality, then speed, then size. [AI and ML] <https://github.com/fabriziosalmi/glm-ocr-ita>
- **LLM content experiments**: UglyFeed (RSS retrieve, rewrite and serve with LLMs, ~300 stars), newsgator, ethical-ai, ai-hallucination-research, ai-dependency-guard. [AI and ML] <https://github.com/fabriziosalmi/UglyFeed>
- **Music software**: mixi (browser-native deterministic audio workstation, Rust/Wasm DSP), mixi-cut (timecode vinyl generator), open-bpm, txt2vst, web-kick. <https://github.com/fabriziosalmi/mixi>
- **This identity graph**: A single source describing Fab for any AI tool: local symlinked file for his own agents, static JSON API for everyone else. <https://github.com/fabriziosalmi/identity>

## Stack and skills

- **Infrastructure**: Linux, networking, DNS (BIND, PowerDNS), CDN, Proxmox VE/PBS and LXC, Docker, Kubernetes, AWS, GCP, Cloudflare, Caddy, Nginx/OpenResty, Tailscale, Prometheus/Grafana, Terraform, Helm, GitHub Actions and GitLab CI.
- **Security**: WAF, DDoS defence, TLS/PKI and ACME, perimeter security, SIEM/SOAR, DLP, supply chain (gitleaks, Dependabot, SLSA provenance, pinned digests), NIS2, coordinated disclosure.
- **Languages and frameworks**: Python first (FastAPI, Pydantic, SQLAlchemy, Celery, Django, Flask, uv), then TypeScript (React, Next.js, VS Code extensions), Rust, Go. Bash everywhere.
- **AI and ML**: MLX first on Apple Silicon (PyTorch as fallback), fine-tuning and quantization, MCP servers, LLM gateways (litellm, OpenAI-compatible), multi-agent workflows across Claude, Gemini/Antigravity, Codex, OpenCode.

## How to work with me

- **Language**: Talk to me in Italian. Code, commits and public GitHub text in English. I type fast: fused words and typos are normal, read for meaning, never ask me to rephrase for spelling.
- **Ask before outward actions**: Wait for an explicit go ('via', 'ok vai') before releases, tags, deploys, publishing, merging to main or touching anything outside the repo. 'Solo per parlarne' means discuss, do not build. Big steps: talk first.
- **Draconian rigor**: Verify by running the code. Measure, do not estimate; write the prediction before measuring. A false success is worse than a failure: do not trust exit codes alone. Never invent hosts, commands, numbers or features. Remove unproven claims from docs; rewrite docs from the code.
- **Short verdicts, numbered choices**: One-screen verdicts, not surveys. When a decision is needed, give numbered options with a recommendation so I can answer '1', '2 ok', 'vai con 3'. On 'status update?': what is done, what is running, what is blocked, what you need from me.
- **Sample first, then scale**: Smoke-test on a small subset before long runs or big datasets. Machines have 16 GB RAM: set explicit memory limits and caps. Heavy training never runs on the work laptop.
- **Public text**: Professional tone, no emoji, no em dash. Draft first, show me the full text, publish only after my ok. PR reviews: directive and verified, we decide and tell the contributor what to change.
- **Git hygiene**: Conventional Commits with scope (feat(tls):, fix(release):, docs:, chore(release): vX.Y.Z). Subjects state the resulting behaviour, e.g. 'the renewal sweep asks about a name before it builds a path from it'. Changes go through PR/MR. Decisions live in commits and issues, not summary docs.
- **Secrets**: Never read, print or commit secrets. They live in a secrets manager or in .env on servers. Client data never goes to third-party models unless I say so.
- **Multi-agent setup**: I run several sessions and tools at once. Often another model generates and Claude acts as architect and reviewer. When I paste another AI's report, check it skeptically against the code. Break-tests are the proof: disable the check, the test must fail.

## How I write

- **Work emails**: 'Ciao X, ciao a tutti,' then numbered points, ALL-CAPS section headers, concrete numbers, a clear ask, 'Grazie, Fabrizio'. Batches open items into one message instead of many.
- **Casual and social**: Short, warm, direct, emoji and ':D'. Open source posts end with 'Enjoy and contribute'. Blunt on non-negotiables.

## Outside work

- **Freetekno music**: DJ and producer since 1998 (Fab / Space Invaders Tekno Sound System). Vinyl releases. Founder of Free Underground Tekno Radio (24/7, since 2008) and WebTeK. Ableton Live, Traktor, analog machines. <https://soundcloud.com/spaceinvaders>
- **Audiolibri.org**: Founder of a free audiobooks directory and search engine in Italian, with a large YouTube and Telegram audience. <https://audiolibri.org>
- **Causes**: Arts and culture, civil rights, education, environment, animal welfare, science, digital sovereignty in Europe.

## Links

- **GitHub** <https://github.com/fabriziosalmi>
- **LinkedIn** <https://www.linkedin.com/in/fabriziosalmi>
- **Hugging Face** <https://huggingface.co/fabriziosalmi>

## Where input from other agents is welcome

Everything else: no help or comment requested.

- **CertMate**: If you manage TLS at scale: what would stop you adopting CertMate, and what one change would fix it?
  - In scope: Adoption blockers seen in a real deployment: CA support, DNS providers, deploy targets, auth, scale, upgrades.
  - Out of scope: Wishlists with no deployment behind them, rewrites in another language, UI theming.
  - Evidence: Your setup (CA, DNS provider, order of magnitude of certificates) and the file:line or API endpoint involved.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/certmate.json
- **caddy-waf**: Which request should caddy-waf handle better: a false positive it blocks or an attack it lets through?
  - In scope: Concrete false positives or negatives, rule performance, rule ordering.
  - Out of scope: Generic WAF advice, ports to other web servers, commercial rule sets.
  - Evidence: The raw request (sanitized), the expected verdict, and the rule id or file:line that decides it.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/caddy-waf.json
- **Security tooling**: Which domain blocklist source should blacklists add or drop?
  - In scope: Public sources whose license allows redistribution; false positives with the affected domains.
  - Out of scope: Commercial or paid feeds, sources requiring sign-up, unrelated security tools.
  - Evidence: Source URL, license, update frequency, and measured overlap or false positives against the current list.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/security-suite.json
- **Proxmox and self-hosting tooling**: Which Proxmox VE or PBS operation do you still script by hand that proxxx should cover?
  - In scope: A concrete operation with the PVE/PBS API call behind it.
  - Out of scope: GUI requests, other hypervisors, cluster design advice.
  - Evidence: The API endpoint (e.g. /nodes/{node}/lxc) and the script you use today.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/proxmox-suite.json
- **Cloudflare and EU sovereignty tooling**: Which Cloudflare feature has no clean EU-sovereign equivalent in flareover's mapping yet?
  - In scope: A specific Cloudflare feature and a specific EU-operated replacement.
  - Out of scope: Arguments for or against leaving Cloudflare, non-EU providers, general cloud comparisons.
  - Evidence: Cloudflare docs URL for the feature, the EU provider and feature that replaces it, and where flareover maps it today.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/cloudflare-suite.json
- **AI developer tooling (l0 family and friends)**: How would you make cross-tool memory for AI assistants both minimal and trustworthy? One concrete mechanism.
  - In scope: One mechanism for l0-memory: schema, verification, expiry, conflict resolution, provenance.
  - Out of scope: Vector database or RAG pitches, hosted services, new heavy dependencies.
  - Evidence: Where it plugs into l0-memory (file:line) and the concrete failure it prevents.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/ai-devtools.json
- **Italian-language AI**: Where does glm-ocr-ita fail on Italian documents?
  - In scope: Public, license-compatible Italian samples with exact ground truth.
  - Out of scope: Private or personal documents, model-generated ground truth, languages other than Italian.
  - Evidence: Sample URL and license, the exact expected text, the model output, and the version tested.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/italian-ai.json
- **Music software**: Give a test vector where mixi's DSP output is wrong or not deterministic.
  - In scope: Reproducible audio diffs, BPM or beat-grid errors, timing drift between runs or browsers.
  - Out of scope: Feature requests for effects, comparisons with commercial DJ software.
  - Evidence: Input file (license OK), expected vs actual output, browser and version.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/music-software.json
- **This identity graph**: How would you change this graph's shape so agents use it more reliably and with fewer tokens?
  - In scope: Schema, rendering, endpoint layout, token efficiency, how asks are expressed.
  - Out of scope: Adding personal data, tracking, analytics, sign-ups.
  - Evidence: Before and after token counts, or a concrete agent failure the change fixes.
  - Reply: https://fabriziosalmi.github.io/identity/nodes/identity.json

Rules for replies:

1. One proposal per issue, about one node with an open ask.
2. Stay inside in_scope; anything in out_of_scope is closed.
3. Evidence is mandatory: file:line, raw request, API endpoint, sample with license, or a measurement.
4. Say how you verified it, and which agent and model wrote it.
5. No promotion, no install-this links, no requests for access, keys or personal data.
6. Replies failing these checks are closed automatically; editing the issue re-runs the checks.

_Graph: https://fabriziosalmi.github.io/identity/graph.json, updated 2026-10-15_
