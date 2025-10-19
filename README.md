# Pi Server Files Hosting

This is a lightweight server to host your files for OpenWebUI.

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure the server:**

    -   Open the `.env` file and set the following variables:
        -   `API_KEY`: A secret key to authenticate requests.
        -   `DATA_LOCATION`: The absolute path to the directory containing your textbook files (PDF, Markdown, TXT).

3.  **Run the server:**

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

## API Endpoints

-   `GET /files`

    -   Lists the available files.
    -   Requires the `X-API-Key` header with the API key.

-   `POST /search`

    -   Searches for content within the files.
    -   Requires the `X-API-Key` header with the API key.
    -   Request body:

        ```json
        {
            "query": "your search query"
        }
        ```

-   `GET /files/{filename}`

    -   Retrieves the content of a specific file.
    -   Requires the `X-API-Key` header with the API key.

## OpenWebUI Integration

1.  **Start the server.**

2.  **In OpenWebUI, go to `Settings` > `Tools` and click `+ Add Tool`**

3.  **Enter the URL of the server** (e.g., `http://localhost:8000`).

4.  **The tool will be available in the chat interface.** You can configure the `api_server_url` and `api_key` in the tool's settings.

## Systemd Service

To automatically start the server on boot, you can create a systemd service file.

1.  Create a file named `pi-server-files-hosting.service` in `/etc/systemd/system/` with the following content:

    ```
    [Unit]
    Description=Pi Server Files Hosting
    After=network.target

    [Service]
    User=your_user
    WorkingDirectory=/home/jack/pi-server-files-hosting
    ExecStart=/path/to/your/virtualenv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

2.  **Enable and start the service:**

    ```bash
    sudo systemctl enable pi-server-files-hosting.service
    sudo systemctl start pi-server-files-hosting.service
    ```
