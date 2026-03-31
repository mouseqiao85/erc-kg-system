import pytest


class TestDocumentAPI:
    
    def test_create_document(self, client, auth_headers):
        project_response = client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "Test"},
            headers=auth_headers
        )
        project_id = project_response.json()["id"]
        
        response = client.post(
            "/api/v1/documents",
            json={
                "project_id": project_id,
                "title": "Test Document",
                "format": "txt",
                "content": "This is a test document content."
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Document"
        assert data["format"] == "txt"
    
    def test_list_documents(self, client, auth_headers):
        project_response = client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "Test"},
            headers=auth_headers
        )
        project_id = project_response.json()["id"]
        
        client.post(
            "/api/v1/documents",
            json={
                "project_id": project_id,
                "title": "Doc 1",
                "format": "txt",
                "content": "Content 1"
            },
            headers=auth_headers
        )
        
        response = client.get(
            "/api/v1/documents",
            params={"project_id": project_id},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_delete_document(self, client, auth_headers):
        project_response = client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "Test"},
            headers=auth_headers
        )
        project_id = project_response.json()["id"]
        
        doc_response = client.post(
            "/api/v1/documents",
            json={
                "project_id": project_id,
                "title": "To Delete",
                "format": "txt",
                "content": "Content"
            },
            headers=auth_headers
        )
        doc_id = doc_response.json()["id"]
        
        response = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
        assert response.status_code == 200
