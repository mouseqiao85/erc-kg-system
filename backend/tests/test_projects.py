import pytest
from uuid import uuid4


class TestProjectAPI:
    
    def test_create_project(self, client, auth_headers):
        response = client.post(
            "/api/v1/projects",
            json={
                "name": "Test Project",
                "description": "A test project"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"
    
    def test_list_projects(self, client, auth_headers):
        client.post(
            "/api/v1/projects",
            json={"name": "Project 1", "description": "Desc 1"},
            headers=auth_headers
        )
        client.post(
            "/api/v1/projects",
            json={"name": "Project 2", "description": "Desc 2"},
            headers=auth_headers
        )
        
        response = client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_get_project(self, client, auth_headers):
        create_response = client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "Test"},
            headers=auth_headers
        )
        project_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Project"
    
    def test_delete_project(self, client, auth_headers):
        create_response = client.post(
            "/api/v1/projects",
            json={"name": "To Delete", "description": "Test"},
            headers=auth_headers
        )
        project_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
    
    def test_create_project_unauthorized(self, client):
        response = client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "Test"}
        )
        assert response.status_code == 401
