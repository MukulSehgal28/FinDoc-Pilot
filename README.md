# Financial Document Crawler

A template-driven financial document acquisition system that discovers, validates, and downloads financial reports from verified company websites.

## Overview

The Financial Document Crawler is designed to automate the collection of financial documents from official company websites, particularly investor relations sections.

The system will allow users to register companies, provide their official website URLs, select a financial year, discover available documents, and download selected files to local storage.

The initial prototype will support five companies, with a modular architecture designed to scale toward 200–2,000 companies.

## Objectives

- Crawl approved company websites without unrestricted internet searching.
- Discover investor relations pages and financial document links.
- Extract actual document filenames and source URLs.
- Filter document candidates by financial year where sufficient evidence exists.
- Allow users to select documents before downloading.
- Validate downloaded files and detect identical file contents.
- Store documents locally and metadata in PostgreSQL.
- Maintain traceability, security, and reliable error handling.
- Support new companies through reusable configurations rather than separate crawler implementations.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Flask | Web application and backend routes |
| Requests | HTTP requests and webpage retrieval |
| BeautifulSoup | HTML parsing and link extraction |
| PostgreSQL | Persistent storage of company, job, and document metadata |
| HTML, CSS, JavaScript | Frontend interface |
| SHA-256 | File integrity identification and duplicate detection |
| PyMuPDF | PDF parsing and text extraction where needed |
| pytest | Automated testing |
| Docker Compose | Reproducible development environment, where useful |

### Optional Future Technologies

- **Playwright:** Browser automation for websites that require JavaScript rendering. Not required for the initial implementation.
- **Celery and Redis:** Background job processing when workload and concurrency justify them.

The initial crawler will use Requests and BeautifulSoup.

## How It Will Work

1. **Register a company:** Enter its name and verified official website URL.
2. **Select a financial year:** Specify the reporting period to investigate.
3. **Crawl the website:** Discover internal links within approved host boundaries.
4. **Identify investor relations pages:** Use configurable rules and link context.
5. **Discover documents:** Extract actual filenames, document URLs, and source pages.
6. **Review results:** Display the discovered candidates to the user.
7. **Select documents:** The user chooses which files to download.
8. **Validate downloads:** Check file signatures, size limits, and format validity.
9. **Store files:** Save validated documents locally and calculate their SHA-256 hashes.
10. **Record metadata:** Store document details, source information, and job status in PostgreSQL.

## Architecture

The application will use a modular, configuration-driven architecture.

```text
Frontend
   |
   v
Flask Backend
   |
   v
Company Configuration
   |
   v
URL Validation and Security
   |
   v
Crawler Engine
   |
   +--> Link Discovery
   |
   +--> Investor Relations Detection
   |
   +--> Document Extraction
   |
   v
Document Review Interface
   |
   v
Secure Download and Validation
   |
   +--> Local File Storage
   |
   +--> PostgreSQL Metadata
```

Company-specific configurations will define approved hostnames, crawl limits, discovery keywords, and supported document formats.

A site-specific adapter may be introduced when a website cannot be handled reliably by the generic crawler.

## Database

PostgreSQL will store structured metadata rather than the actual document files.

Planned entities include:

- **Companies:** Names, approved website URLs, configurations, and active status.
- **Crawl Jobs:** Requested financial years, progress, timestamps, and errors.
- **Discovered URLs:** Visited pages, crawl depth, and discovery status.
- **Documents:** Original filenames, source URLs, reporting periods, file hashes, storage locations, and validation status.

The actual documents will initially be stored on the local filesystem.

## Security Requirements

Security is a core design requirement.

The system should:

- Validate starting URLs and approved hostnames.
- Restrict requests to permitted destinations.
- Validate DNS destinations and every redirect.
- Block access to localhost, private networks, and prohibited endpoints.
- Enforce timeouts, page limits, file-size limits, and crawl-rate limits.
- Validate downloaded content rather than trusting file extensions.
- Generate safe internal filenames and prevent path traversal.
- Store documents outside the public web directory.
- Use parameterized database operations.
- Protect frontend actions against unauthorized access and CSRF.
- Keep credentials and API keys out of source control.
- Record errors without exposing secrets or sensitive server information.

The crawler must not bypass authentication, CAPTCHAs, access controls, or applicable website restrictions.

## Deduplication

The system will distinguish between three types of duplication:

1. **URL deduplication:** Avoid repeatedly visiting the same normalized URL.
2. **Record deduplication:** Avoid creating duplicate document metadata records.
3. **Content deduplication:** Use SHA-256 to identify files with identical contents.

Identical filenames do not guarantee identical files, and a URL may serve updated content over time.

## Planned Development Stages

### Phase 1 — Foundation
- Establish the repository and project structure.
- Configure Python and Flask.
- Connect PostgreSQL.
- Create database models and migrations.

### Phase 2 — URL Security
- Implement URL validation.
- Enforce approved hostnames.
- Validate redirects and network destinations.
- Add security tests.

### Phase 3 — Web Crawling
- Implement HTTP fetching and link extraction.
- Normalize URLs and track visited pages.
- Add crawl-depth, page-count, and time limits.

### Phase 4 — Document Discovery
- Identify investor relations pages.
- Extract document names and links.
- Implement reporting-period matching.
- Display discovered candidates.

### Phase 5 — Secure Downloads
- Implement controlled file downloads.
- Validate document formats.
- Calculate SHA-256 hashes.
- Store files and metadata.

### Phase 6 — Frontend
- Build company registration.
- Add financial-year selection.
- Display crawl results and job status.
- Allow user-selected downloads.

### Phase 7 — Testing and Expansion
- Validate the workflow against five company websites.
- Add regression and security tests.
- Improve reusable configurations.
- Measure performance before scaling.

## Testing Strategy

Automated tests will cover:

- URL normalization and hostname validation.
- Redirect restrictions and private-network blocking.
- Link extraction and crawl limits.
- Investor-page detection.
- Filename extraction and financial-year matching.
- File-size and signature validation.
- Duplicate detection and database constraints.
- Interrupted downloads and network failures.
- Database errors and job recovery.
- End-to-end document discovery and user-selected downloads.

Routine tests should use local fixtures and mocked HTTP responses wherever practical.

## Project Status

**Current stage:** Planning and initial development.

The architecture and implementation roadmap have been defined. Individual features should be marked complete only after implementation and appropriate testing.

## Future Scope

- Support additional companies through reusable configurations.
- Introduce background workers for larger workloads.
- Improve monitoring, retries, and crawl scheduling.
- Add document version history and integrity checks.
- Improve reporting-period identification.
- Evaluate additional storage and deployment options as requirements grow.

## Guiding Principles

- Security before convenience.
- Reusable architecture over duplicated code.
- Deterministic crawling without an AI dependency.
- Explicit user selection before downloading.
- Traceable document sources.
- Testable components and documented failure handling.
- Measured scaling rather than premature complexity.

---

**Note:** This project is intended to assist with collecting financial documents. It does not initially perform fundamental analysis, provide investment recommendations, or guarantee that every document discovered is authentic or correctly classified. Source verification and reporting-period validation remain important.
