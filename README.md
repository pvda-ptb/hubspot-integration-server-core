# HubSpot Integration Core

## Overview

The HubSpot Integration Core serves as the foundational framework for building modular, reusable integrations with HubSpot and potentially other platforms, such as `PlaceholderSyncTarget`. This core handles essential functionalities like OAuth authentication, database connectivity, and webhook processing, allowing specific integrations to focus on custom logic and business-specific requirements.

## Design Philosophy

- **Modularity**: The structure promotes separation of concerns, where core functionalities are encapsulated within this core, reducing redundancy across specific integrations.
- **Scalability**: By abstracting common logic to a core library, new integrations can be quickly developed and deployed.
- **Extensibility**: Designed to be extended for additional services or webhook handling, allowing developers to customize and build upon the existing core.

## Features

- **OAuth Authentication**: Simplifies handling authentication processes with HubSpot and stores tokens securely.
- **Database Management**: Uses SQLAlchemy for ORM, facilitating database interactions and migrations.
- **Webhook Handlers**: Provides base handlers for managing incoming requests from HubSpot, expandable for other services.

## Installation and Setup

1. **Clone the Repository**:
   ```bash
   git clone <core-repo-url>
   cd hubspot_integration_core
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables**:

Define environment configurations in a .env file.

4. **Run Database Migrations**:

    ```
    python -m app.init_db
    ```

5. **Start the Application**:

Launch the application using Docker Compose:

    ```bash
    docker-compose up --build
    ```

## Usage Notes
This core is intended to be used in tandem with specific integrations that implement additional service-specific logic. Developers should structure their integration following a similar modular design, utilizing this core for widespread reusable components.