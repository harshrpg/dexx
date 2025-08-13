# Project Structure Replication Instructions

## Overview
Create a new project with the exact same structure as Langflow, a full-stack application with Python backend, React frontend, comprehensive testing, CI/CD, documentation, and deployment infrastructure.

## Project Structure

### Root Directory Structure
```
project-name/
├── .git/                          # Git repository
├── .github/                       # GitHub workflows and configurations
├── .devcontainer/                 # VS Code devcontainer configuration
├── .vscode/                       # VS Code settings
├── .cursor/                       # Cursor IDE settings
├── src/                           # Main source code
├── docs/                          # Documentation (Docusaurus)
├── docker/                        # Docker configurations
├── docker_example/                # Docker compose examples
├── deploy/                        # Deployment configurations
├── scripts/                       # Utility scripts
├── test-results/                  # Test output directory
├── .gitignore                     # Git ignore rules
├── .gitattributes                 # Git attributes
├── .pre-commit-config.yaml        # Pre-commit hooks
├── .eslintrc.json                 # ESLint configuration
├── .composio.lock                 # Composio lock file
├── .coderabbit.yaml               # CodeRabbit configuration
├── eslint.config.js               # ESLint configuration
├── pyproject.toml                 # Python project configuration
├── uv.lock                        # UV lock file
├── Makefile                       # Main Makefile
├── Makefile.frontend              # Frontend-specific Makefile
├── README.md                      # Project README
├── CONTRIBUTING.md                # Contribution guidelines
├── DEVELOPMENT.md                 # Development setup guide
├── CODE_OF_CONDUCT.md             # Code of conduct
├── SECURITY.md                    # Security policy
├── LICENSE                        # License file
├── render.yaml                    # Render deployment config
└── cdk.Dockerfile                 # CDK Docker configuration
```

### Source Code Structure (`src/`)
```
src/
├── backend/                       # Backend Python code
│   ├── base/                      # Base package
│   │   ├── langflow/              # Main backend package
│   │   │   ├── __init__.py
│   │   │   ├── __main__.py        # Entry point
│   │   │   ├── main.py            # Main application
│   │   │   ├── server.py          # Server configuration
│   │   │   ├── worker.py          # Worker processes
│   │   │   ├── memory.py          # Memory management
│   │   │   ├── middleware.py      # Middleware
│   │   │   ├── settings.py        # Settings configuration
│   │   │   ├── py.typed           # Type hints marker
│   │   │   ├── alembic.ini        # Database migrations
│   │   │   ├── api/               # API endpoints
│   │   │   ├── base/              # Base classes
│   │   │   ├── cli/               # Command line interface
│   │   │   ├── components/        # Component definitions
│   │   │   ├── core/              # Core functionality
│   │   │   ├── custom/            # Custom components
│   │   │   ├── events/            # Event handling
│   │   │   ├── exceptions/        # Custom exceptions
│   │   │   ├── field_typing/      # Field type definitions
│   │   │   ├── graph/             # Graph processing
│   │   │   ├── helpers/           # Helper functions
│   │   │   ├── initial_setup/     # Initialization
│   │   │   ├── inputs/            # Input handling
│   │   │   ├── interface/         # Interface definitions
│   │   │   ├── io/                # Input/output handling
│   │   │   ├── legacy_custom/     # Legacy custom code
│   │   │   ├── load/              # Loading functionality
│   │   │   ├── logging/           # Logging configuration
│   │   │   ├── processing/        # Data processing
│   │   │   ├── schema/            # Data schemas
│   │   │   ├── serialization/     # Serialization logic
│   │   │   ├── services/          # Service layer
│   │   │   ├── template/          # Templates
│   │   │   ├── type_extraction/   # Type extraction
│   │   │   ├── utils/             # Utility functions
│   │   │   └── version/           # Version management
│   │   ├── pyproject.toml         # Backend package config
│   │   ├── uv.lock                # Backend dependencies
│   │   └── README.md              # Backend README
│   ├── tests/                     # Backend tests
│   └── .gitignore                 # Backend gitignore
└── frontend/                      # Frontend React code
    ├── src/                       # Frontend source
    │   ├── components/            # React components
    │   ├── pages/                 # Page components
    │   ├── hooks/                 # Custom React hooks
    │   ├── stores/                # State management
    │   ├── utils/                 # Utility functions
    │   ├── types/                 # TypeScript types
    │   ├── constants/             # Constants
    │   ├── contexts/              # React contexts
    │   ├── helpers/               # Helper functions
    │   ├── controllers/           # API controllers
    │   ├── modals/                # Modal components
    │   ├── icons/                 # Icon components
    │   ├── alerts/                # Alert components
    │   ├── CustomNodes/           # Custom flow nodes
    │   ├── CustomEdges/           # Custom flow edges
    │   ├── shared/                # Shared components
    │   ├── boilerplate/           # Boilerplate code
    │   ├── assets/                # Static assets
    │   ├── style/                 # Styling
    │   ├── customization/         # Customization options
    │   ├── App.tsx                # Main App component
    │   ├── App.css                # App styles
    │   ├── index.tsx              # Entry point
    │   ├── routes.tsx             # Routing configuration
    │   ├── flow_constants.tsx     # Flow constants
    │   ├── setupTests.ts          # Test setup
    │   ├── reportWebVitals.ts     # Performance monitoring
    │   ├── vite-env.d.ts          # Vite environment types
    │   ├── svg.d.ts               # SVG type definitions
    │   └── png.d.ts               # PNG type definitions
    ├── public/                    # Public assets
    ├── tests/                     # Frontend tests
    ├── package.json               # Frontend dependencies
    ├── package-lock.json          # Lock file
    ├── tsconfig.json              # TypeScript config
    ├── vite.config.mts            # Vite configuration
    ├── tailwind.config.mjs        # Tailwind CSS config
    ├── postcss.config.js          # PostCSS config
    ├── jest.config.js             # Jest configuration
    ├── playwright.config.ts       # Playwright config
    ├── .eslintrc.json             # ESLint config
    ├── .prettierrc.mjs            # Prettier config
    ├── .prettierignore            # Prettier ignore
    ├── .dockerignore              # Docker ignore
    ├── Dockerfile                 # Frontend Dockerfile
    ├── cdk.Dockerfile             # CDK Dockerfile
    ├── dev.Dockerfile             # Development Dockerfile
    ├── nginx.conf                 # Nginx configuration
    ├── index.html                 # HTML template
    ├── start-nginx.sh             # Nginx startup script
    ├── set_proxy.sh               # Proxy setup script
    ├── run-tests.sh               # Test runner script
    ├── README.md                  # Frontend README
    └── .gitignore                 # Frontend gitignore
```

### Documentation Structure (`docs/`)
```
docs/
├── src/                           # Documentation source
├── static/                        # Static assets
├── css/                           # Custom styles
├── i18n/                          # Internationalization
├── docs/                          # Documentation content
├── package.json                   # Docusaurus dependencies
├── package-lock.json              # Lock file
├── yarn.lock                      # Yarn lock file
├── docusaurus.config.js           # Docusaurus configuration
├── sidebars.js                    # Sidebar configuration
├── tailwind.config.js             # Tailwind config
├── tsconfig.json                  # TypeScript config
├── babel.config.js                # Babel config
├── .yarnrc.yml                    # Yarn configuration
├── .gitignore                     # Documentation gitignore
├── index.d.ts                     # Type definitions
├── openapi.json                   # OpenAPI specification
└── README.md                      # Documentation README
```

### GitHub Workflows (`.github/`)
```
.github/
├── workflows/                     # CI/CD workflows
│   ├── ci.yml                     # Main CI pipeline
│   ├── python_test.yml            # Python tests
│   ├── typescript_test.yml        # TypeScript tests
│   ├── jest_test.yml              # Jest tests
│   ├── integration_tests.yml      # Integration tests
│   ├── docker_test.yml            # Docker tests
│   ├── docs_test.yml              # Documentation tests
│   ├── release.yml                # Release workflow
│   ├── release_nightly.yml        # Nightly releases
│   ├── nightly_build.yml          # Nightly builds
│   ├── docker-build.yml           # Docker builds
│   ├── deploy-docs-draft.yml      # Documentation deployment
│   ├── deploy_gh-pages.yml        # GitHub Pages deployment
│   ├── lint-py.yml                # Python linting
│   ├── lint-js.yml                # JavaScript linting
│   ├── style-check-py.yml         # Python style checks
│   ├── py_autofix.yml             # Python auto-fix
│   ├── js_autofix.yml             # JavaScript auto-fix
│   ├── codeql.yml                 # CodeQL security
│   ├── codeflash.yml              # CodeFlash analysis
│   ├── create-release.yml         # Release creation
│   ├── add-labels.yml             # Issue labeling
│   ├── conventional-labels.yml    # Conventional labels
│   ├── auto-update.yml            # Auto-updates
│   ├── fetch_docs_notion.yml      # Notion docs sync
│   ├── docs-update-openapi.yml    # OpenAPI docs update
│   ├── store_pytest_durations.yml # Test duration tracking
│   └── matchers/                  # Workflow matchers
├── ISSUE_TEMPLATE/                # Issue templates
├── actions/                       # Custom GitHub actions
├── semantic.yml                   # Semantic release config
├── changes-filter.yaml            # Changes filter
├── dependabot.yml                 # Dependabot configuration
└── release.yml                    # Release configuration
```

### Docker Structure (`docker/`)
```
docker/
├── frontend/                      # Frontend Docker files
├── .dockerignore                  # Docker ignore rules
├── build_and_push.Dockerfile      # Main build Dockerfile
├── build_and_push_backend.Dockerfile # Backend Dockerfile
├── build_and_push_base.Dockerfile # Base Dockerfile
├── build_and_push_ep.Dockerfile   # Endpoint Dockerfile
├── build_and_push_with_extras.Dockerfile # Extras Dockerfile
├── cdk.Dockerfile                 # CDK Dockerfile
├── dev.Dockerfile                 # Development Dockerfile
├── render.Dockerfile              # Render deployment
├── render.pre-release.Dockerfile  # Pre-release Dockerfile
├── cdk-docker-compose.yml         # CDK compose
├── dev.docker-compose.yml         # Development compose
├── container-cmd-cdk.sh           # CDK container command
└── dev.start.sh                   # Development startup
```

## Implementation Instructions

### 1. Project Initialization
1. Create the root directory structure
2. Initialize Git repository -> DONE
3. Set up Python project with `pyproject.toml`
4. Set up Node.js project with `package.json`
5. Configure development tools (ESLint, Prettier, etc.)

### 2. Backend Setup
1. Create Python package structure in `src/backend/base/`
2. Set up FastAPI application structure
3. Configure database models and migrations
4. Set up API endpoints and routing
5. Implement component system
6. Add testing framework (pytest)
7. Configure logging and error handling

### 3. Frontend Setup
1. Create React application with TypeScript
2. Set up Vite as build tool
3. Configure Tailwind CSS
4. Set up state management (Zustand)
5. Implement routing with React Router
6. Add component library (Radix UI)
7. Set up testing with Jest and Playwright
8. Configure ESLint and Prettier

### 4. Documentation Setup
1. Initialize Docusaurus project
2. Configure documentation structure
3. Set up API documentation generation
4. Add internationalization support
5. Configure deployment to GitHub Pages

### 5. CI/CD Pipeline
1. Set up GitHub Actions workflows
2. Configure automated testing
3. Set up Docker builds
4. Configure deployment pipelines
5. Add security scanning
6. Set up automated releases

### 6. Development Tools
1. Configure VS Code devcontainer
2. Set up pre-commit hooks
3. Add Makefile for common tasks
4. Configure Docker development environment
5. Set up hot reloading for development

### 7. Testing Infrastructure
1. Set up unit tests for backend
2. Set up integration tests
3. Configure frontend testing
4. Set up end-to-end testing
5. Add performance testing
6. Configure test coverage reporting

### 8. Deployment Configuration
1. Set up Docker production builds
2. Configure cloud deployment (Render, etc.)
3. Set up CDN and static asset serving
4. Configure environment management
5. Set up monitoring and logging

## Key Configuration Files

### Python Configuration (`pyproject.toml`)
- Project metadata and dependencies
- Build system configuration
- Development dependencies
- Testing configuration
- Linting and formatting tools

### Frontend Configuration (`package.json`)
- Dependencies and scripts
- Build tools configuration
- Testing framework setup
- Development server configuration

### Build Tools
- Vite for frontend bundling
- UV for Python dependency management
- Make for task automation
- Docker for containerization

### Code Quality
- ESLint for JavaScript/TypeScript
- Prettier for code formatting
- Black for Python formatting
- MyPy for Python type checking
- Pre-commit hooks for automated checks

### Testing
- Jest for JavaScript testing
- Playwright for end-to-end testing
- Pytest for Python testing
- Coverage reporting
- Performance testing

### Documentation
- Docusaurus for documentation site
- OpenAPI for API documentation
- JSDoc for JavaScript documentation
- TypeDoc for TypeScript documentation

## Development Workflow

1. **Setup**: Run `make init` to install all dependencies
2. **Development**: Use `make dev` to start development servers
3. **Testing**: Run `make test` to execute all tests
4. **Building**: Use `make build` to create production builds
5. **Deployment**: Use `make deploy` to deploy to production

## Notes
- Maintain the exact directory structure and file organization
- Use the same naming conventions and patterns
- Implement similar build and deployment processes
- Follow the same testing and quality assurance practices
- Use equivalent tools and technologies where appropriate
- Adapt the content and functionality for your specific project needs 