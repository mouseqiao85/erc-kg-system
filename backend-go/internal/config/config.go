package config

import (
	"fmt"
	"os"

	"github.com/spf13/viper"
)

type Config struct {
	Port             int
	LogLevel         string
	JWT              JWTConfig
	Database         DatabaseConfig
	Neo4j           Neo4jConfig
	Redis           RedisConfig
	PythonBackendURL string
}

type JWTConfig struct {
	Secret     string
	ExpiryHours int
}

type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
	SSLMode  string
}

type Neo4jConfig struct {
	URI      string
	Username string
	Password string
}

type RedisConfig struct {
	Host     string
	Port     int
	Password string
	DB       int
}

func Load() (*Config, error) {
	// Set default values
	viper.SetDefault("PORT", 8000)
	viper.SetDefault("LOG_LEVEL", "info")
	viper.SetDefault("JWT_SECRET", "your-secret-key-change-in-production")
	viper.SetDefault("JWT_EXPIRY_HOURS", 24)
	viper.SetDefault("DB_HOST", "localhost")
	viper.SetDefault("DB_PORT", 5432)
	viper.SetDefault("DB_USER", "postgres")
	viper.SetDefault("DB_PASSWORD", "postgres")
	viper.SetDefault("DB_NAME", "erc_kg")
	viper.SetDefault("DB_SSL_MODE", "disable")
	viper.SetDefault("NEO4J_URI", "bolt://localhost:7687")
	viper.SetDefault("NEO4J_USERNAME", "neo4j")
	viper.SetDefault("NEO4J_PASSWORD", "neo4j")
	viper.SetDefault("REDIS_HOST", "localhost")
	viper.SetDefault("REDIS_PORT", 6379)
	viper.SetDefault("REDIS_PASSWORD", "")
	viper.SetDefault("REDIS_DB", 0)
	viper.SetDefault("PYTHON_BACKEND_URL", "http://localhost:8001")

	// Read from environment variables
	viper.AutomaticEnv()

	// Read config file if exists
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath("./config")
	viper.AddConfigPath(".")

	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("error reading config file: %w", err)
		}
	}

	cfg := &Config{
		Port:     viper.GetInt("PORT"),
		LogLevel: viper.GetString("LOG_LEVEL"),
		JWT: JWTConfig{
			Secret:      viper.GetString("JWT_SECRET"),
			ExpiryHours: viper.GetInt("JWT_EXPIRY_HOURS"),
		},
		Database: DatabaseConfig{
			Host:     viper.GetString("DB_HOST"),
			Port:     viper.GetInt("DB_PORT"),
			User:     viper.GetString("DB_USER"),
			Password: viper.GetString("DB_PASSWORD"),
			DBName:   viper.GetString("DB_NAME"),
			SSLMode:  viper.GetString("DB_SSL_MODE"),
		},
		Neo4j: Neo4jConfig{
			URI:      viper.GetString("NEO4J_URI"),
			Username: viper.GetString("NEO4J_USERNAME"),
			Password: viper.GetString("NEO4J_PASSWORD"),
		},
		Redis: RedisConfig{
			Host:     viper.GetString("REDIS_HOST"),
			Port:     viper.GetInt("REDIS_PORT"),
			Password: viper.GetString("REDIS_PASSWORD"),
			DB:       viper.GetInt("REDIS_DB"),
		},
		PythonBackendURL: viper.GetString("PYTHON_BACKEND_URL"),
	}

	// Override with environment variables if set
	if port := os.Getenv("PORT"); port != "" {
		fmt.Sscanf(port, "%d", &cfg.Port)
	}

	return cfg, nil
}
