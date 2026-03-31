import pytest
from passlib.context import CryptContext
from app.models.database import User, Project, Document, Entity, Triple
from uuid import uuid4

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestUserModel:
    
    def test_create_user(self, db_session):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=pwd_context.hash("password123"),
            role="user"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "user"
    
    def test_user_unique_username(self, db_session):
        user1 = User(
            username="duplicate",
            email="user1@example.com",
            password_hash="hash1"
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            username="duplicate",
            email="user2@example.com",
            password_hash="hash2"
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):
            db_session.commit()


class TestProjectModel:
    
    def test_create_project(self, db_session):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            user_id=user.id,
            name="Test Project",
            description="A test project"
        )
        db_session.add(project)
        db_session.commit()
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.user.username == "testuser"


class TestEntityModel:
    
    def test_create_entity(self, db_session):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            user_id=user.id,
            name="Test Project"
        )
        db_session.add(project)
        db_session.commit()
        
        entity = Entity(
            project_id=project.id,
            name="Test Entity",
            type="Person",
            confidence=0.95
        )
        db_session.add(entity)
        db_session.commit()
        
        assert entity.id is not None
        assert entity.name == "Test Entity"
        assert entity.type == "Person"
        assert entity.confidence == 0.95


class TestTripleModel:
    
    def test_create_triple(self, db_session):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash"
        )
        db_session.add(user)
        db_session.commit()
        
        project = Project(
            user_id=user.id,
            name="Test Project"
        )
        db_session.add(project)
        db_session.commit()
        
        head = Entity(
            project_id=project.id,
            name="Entity A",
            type="Person"
        )
        tail = Entity(
            project_id=project.id,
            name="Entity B",
            type="Organization"
        )
        db_session.add_all([head, tail])
        db_session.commit()
        
        triple = Triple(
            project_id=project.id,
            head_id=head.id,
            relation="works_for",
            tail_id=tail.id,
            confidence=0.9
        )
        db_session.add(triple)
        db_session.commit()
        
        assert triple.id is not None
        assert triple.relation == "works_for"
        assert triple.head.name == "Entity A"
        assert triple.tail.name == "Entity B"
