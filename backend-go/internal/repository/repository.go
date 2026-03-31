package repository

import (
	"context"
	"fmt"

	"github.com/redis/go-redis/v9"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	
	"github.com/erc-kg/backend-go/internal/config"
	"github.com/erc-kg/backend-go/internal/models"
)

type UserRepository struct {
	db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
	return &UserRepository{db: db}
}

type ProjectRepository struct {
	db *gorm.DB
}

func NewProjectRepository(db *gorm.DB) *ProjectRepository {
	return &ProjectRepository{db: db}
}

type DocumentRepository struct {
	db *gorm.DB
}

func NewDocumentRepository(db *gorm.DB) *DocumentRepository {
	return &DocumentRepository{db: db}
}

type EntityRepository struct {
	db *gorm.DB
}

func NewEntityRepository(db *gorm.DB) *EntityRepository {
	return &EntityRepository{db: db}
}

type GraphRepository struct {
	driver neo4j.Driver
}

func NewGraphRepository(driver neo4j.Driver) *GraphRepository {
	return &GraphRepository{driver: driver}
}

func NewPostgresDB(cfg config.DatabaseConfig) (*gorm.DB, error) {
	dsn := fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.DBName, cfg.SSLMode,
	)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	// Auto migrate
	err = db.AutoMigrate(&models.User{}, &models.Project{}, &models.Document{}, &models.Entity{})
	if err != nil {
		return nil, err
	}

	return db, nil
}

func NewNeo4jDriver(cfg config.Neo4jConfig) (neo4j.Driver, error) {
	driver, err := neo4j.NewDriver(cfg.URI, neo4j.BasicAuth(cfg.Username, cfg.Password, ""))
	if err != nil {
		return nil, err
	}

	// Test connection
	err = driver.VerifyConnectivity()
	if err != nil {
		return nil, err
	}

	return driver, nil
}

func NewRedisClient(cfg config.RedisConfig) (*redis.Client, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:%d", cfg.Host, cfg.Port),
		Password: cfg.Password,
		DB:       cfg.DB,
	})

	// Test connection
	_, err := client.Ping(context.Background()).Result()
	if err != nil {
		return nil, err
	}

	return client, nil
}
