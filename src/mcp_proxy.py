import os
import httpx
from fastmcp import FastMCP

OPENPROJECT_URL = os.environ.get("OPENPROJECT_URL", "").rstrip("/")

mcp = FastMCP("OpenProject")

def get_client(api_key: str) -> httpx.Client:
    return httpx.Client(
        base_url=f"{OPENPROJECT_URL}/api/v3",
        auth=("apikey", api_key),
        headers={"Content-Type": "application/json"},
        timeout=30.0
    )

@mcp.tool()
def list_projects(api_key: str) -> dict:
    """List all OpenProject projects. api_key is the user's OpenProject API token."""
    with get_client(api_key) as c:
        r = c.get("/projects")
        r.raise_for_status()
        return r.json()

@mcp.tool()
def get_project(api_key: str, project_id: int) -> dict:
    """Get a specific project by ID. api_key is the user's OpenProject API token."""
    with get_client(api_key) as c:
        r = c.get(f"/projects/{project_id}")
        r.raise_for_status()
        return r.json()

@mcp.tool()
def list_work_packages(api_key: str, project_id: int) -> dict:
    """List all work packages in a project. api_key is the user's OpenProject API token."""
    with get_client(api_key) as c:
        r = c.get(f"/projects/{project_id}/work_packages")
        r.raise_for_status()
        return r.json()

@mcp.tool()
def create_work_package(
    api_key: str,
    project_id: int,
    subject: str,
    type_name: str = "Task",
    description: str = "",
    assignee_id: int = None
) -> dict:
    """
    Create a work package in a project.
    api_key is the user's OpenProject API token.
    type_name can be Epic, Story, Task, Milestone etc.
    """
    with get_client(api_key) as c:
        types_r = c.get(f"/projects/{project_id}/types")
        types_r.raise_for_status()
        types = types_r.json().get("_embedded", {}).get("elements", [])
        type_id = next(
            (t["id"] for t in types if t["name"].lower() == type_name.lower()),
            types[0]["id"] if types else None
        )
        payload = {
            "subject": subject,
            "description": {"raw": description},
            "_links": {
                "type": {"href": f"/api/v3/types/{type_id}"},
                "project": {"href": f"/api/v3/projects/{project_id}"}
            }
        }
        if assignee_id:
            payload["_links"]["assignee"] = {"href": f"/api/v3/users/{assignee_id}"}
        r = c.post(f"/projects/{project_id}/work_packages", json=payload)
        r.raise_for_status()
        return r.json()

@mcp.tool()
def list_users(api_key: str) -> dict:
    """List all users in the OpenProject instance. api_key is the user's OpenProject API token."""
    with get_client(api_key) as c:
        r = c.get("/users")
        r.raise_for_status()
        return r.json()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
