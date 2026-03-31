package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/erc-kg/backend-go/internal/api/handlers"
	"github.com/erc-kg/backend-go/internal/api/middleware"
	"github.com/erc-kg/backend-go/internal/config"
	"github.com/erc-kg/backend-go/internal/repository"
	"github.com/erc-kg/backend-go/internal/services"
	"github.com/erc-kg/backend-go/pkg/logger"
)

func main() {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Initialize logger
	logger.Init(cfg.LogLevel)
	logger.Info("Starting ERC-KG Golang Backend...")

	// Initialize database connections
	db, err := repository.NewPostgresDB(cfg.Database)
	if err != nil {
		logger.Fatal("Failed to connect to PostgreSQL", "error", err)
	}
	defer db.Close()

	neo4jDriver, err := repository.NewNeo4jDriver(cfg.Neo4j)
	if err != nil {
		logger.Fatal("Failed to connect to Neo4j", "error", err)
	}
	defer neo4jDriver.Close()

	redisClient, err := repository.NewRedisClient(cfg.Redis)
	if err != nil {
		logger.Fatal("Failed to connect to Redis", "error", err)
	}
	defer redisClient.Close()

	// Initialize repositories
	userRepo := repository.NewUserRepository(db)
	projectRepo := repository.NewProjectRepository(db)
	documentRepo := repository.NewDocumentRepository(db)
	entityRepo := repository.NewEntityRepository(db)
	graphRepo := repository.NewGraphRepository(neo4jDriver)

	// Initialize services
	authService := services.NewAuthService(userRepo, cfg.JWT)
	userService := services.NewUserService(userRepo)
	projectService := services.NewProjectService(projectRepo)
	documentService := services.NewDocumentService(documentRepo)
	entityService := services.NewEntityService(entityRepo)
	graphService := services.NewGraphService(graphRepo)
	pythonService := services.NewPythonService(cfg.PythonBackendURL)

	// Initialize handlers
	authHandler := handlers.NewAuthHandler(authService)
	userHandler := handlers.NewUserHandler(userService)
	projectHandler := handlers.NewProjectHandler(projectService)
	documentHandler := handlers.NewDocumentHandler(documentService)
	entityHandler := handlers.NewEntityHandler(entityService)
	graphHandler := handlers.NewGraphHandler(graphService)
	analyzeHandler := handlers.NewAnalyzeHandler(pythonService)

	// Setup Gin router
	router := gin.Default()

	// Middleware
	router.Use(middleware.CORS())
	router.Use(middleware.Logger())
	router.Use(middleware.Recovery())

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "golang-backend",
			"version": "1.0.0",
		})
	})

	// API routes
	api := router.Group("/api/v1")
	{
		// Auth routes
		auth := api.Group("/auth")
		{
			auth.POST("/register", authHandler.Register)
			auth.POST("/login", authHandler.Login)
			auth.POST("/logout", middleware.AuthRequired(), authHandler.Logout)
			auth.POST("/refresh", authHandler.RefreshToken)
		}

		// User routes
		users := api.Group("/users")
		users.Use(middleware.AuthRequired())
		{
			users.GET("", userHandler.List)
			users.GET("/:id", userHandler.GetByID)
			users.PUT("/:id", userHandler.Update)
			users.DELETE("/:id", userHandler.Delete)
		}

		// Project routes
		projects := api.Group("/projects")
		projects.Use(middleware.AuthRequired())
		{
			projects.GET("", projectHandler.List)
			projects.POST("", projectHandler.Create)
			projects.GET("/:id", projectHandler.GetByID)
			projects.PUT("/:id", projectHandler.Update)
			projects.DELETE("/:id", projectHandler.Delete)
		}

		// Document routes
		documents := api.Group("/documents")
		documents.Use(middleware.AuthRequired())
		{
			documents.GET("", documentHandler.List)
			documents.POST("", documentHandler.Create)
			documents.GET("/:id", documentHandler.GetByID)
			documents.DELETE("/:id", documentHandler.Delete)
		}

		// Entity routes
		entities := api.Group("/entities")
		entities.Use(middleware.AuthRequired())
		{
			entities.GET("", entityHandler.List)
			entities.POST("", entityHandler.Create)
			entities.GET("/:id", entityHandler.GetByID)
			entities.DELETE("/:id", entityHandler.Delete)
		}

		// Graph routes
		graph := api.Group("/graph")
		graph.Use(middleware.AuthRequired())
		{
			graph.GET("/nodes", graphHandler.GetNodes)
			graph.GET("/edges", graphHandler.GetEdges)
			graph.POST("/query", graphHandler.Query)
		}

		// Analyze routes (forward to Python backend)
		analyze := api.Group("/analyze")
		analyze.Use(middleware.AuthRequired())
		{
			analyze.POST("/sentiment", analyzeHandler.Sentiment)
			analyze.POST("/entities", analyzeHandler.Entities)
			analyze.POST("/relations", analyzeHandler.Relations)
		}
	}

	// Start server
	srv := &http.Server{
		Addr:    fmt.Sprintf(":%d", cfg.Port),
		Handler: router,
	}

	// Graceful shutdown
	go func() {
		logger.Info("Server starting", "port", cfg.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Failed to start server", "error", err)
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatal("Server forced to shutdown", "error", err)
	}

	logger.Info("Server exited")
}
